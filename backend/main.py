from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
import random

from database import SessionLocal, engine, Base
from models import User, Track, TrackParticipant, Assignment, Submission, Review, Comment
from schemas import (
    UserCreate, UserResponse, TrackCreate, TrackResponse, AssignmentResponse,
    SubmissionCreate, ReviewCreate, CommentCreate
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_db
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/tracks", response_model=List[TrackResponse])
def get_tracks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tracks = db.query(Track).all()
    result = []
    for track in tracks:
        count = db.query(TrackParticipant).filter(TrackParticipant.track_id == track.id).count()
        result.append({
            "id": track.id,
            "title": track.title,
            "description": track.description,
            "quota": track.quota,
            "started_at": track.started_at,
            "participant_count": count
        })
    return result

@app.post("/tracks", response_model=TrackResponse)
def create_track(track: TrackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_track = Track(
        title=track.title,
        description=track.description,
        quota=track.quota,
        criteria=track.criteria
    )
    db.add(db_track)
    db.flush()
    
    for assn in track.assignments:
        db_assn = Assignment(
            track_id=db_track.id,
            title=assn["title"],
            description=assn["description"],
            deadline_days=assn["deadline_days"],
            order=assn["order"]
        )
        db.add(db_assn)
    
    db.commit()
    db.refresh(db_track)
    return {"id": db_track.id, "title": db_track.title, "description": db_track.description,
            "quota": db_track.quota, "started_at": None, "participant_count": 0}

@app.post("/tracks/{track_id}/join")
def join_track(track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    if track.started_at:
        raise HTTPException(status_code=400, detail="Track already started")
    
    existing = db.query(TrackParticipant).filter(
        TrackParticipant.track_id == track_id,
        TrackParticipant.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already joined")
    
    participant = TrackParticipant(user_id=current_user.id, track_id=track_id)
    db.add(participant)
    
    count = db.query(TrackParticipant).filter(TrackParticipant.track_id == track_id).count() + 1
    if count >= track.quota:
        track.started_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Joined successfully"}

@app.post("/tracks/{track_id}/leave")
def leave_track(track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    if track.started_at:
        raise HTTPException(status_code=400, detail="Cannot leave started track")
    
    participant = db.query(TrackParticipant).filter(
        TrackParticipant.track_id == track_id,
        TrackParticipant.user_id == current_user.id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Not a participant")
    
    db.delete(participant)
    db.commit()
    return {"message": "Left successfully"}

@app.get("/tracks/{track_id}/assignments", response_model=List[AssignmentResponse])
def get_assignments(track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    participant = db.query(TrackParticipant).filter(
        TrackParticipant.track_id == track_id,
        TrackParticipant.user_id == current_user.id
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")
    
    if not track.started_at:
        return []
    
    assignments = db.query(Assignment).filter(Assignment.track_id == track_id).order_by(Assignment.order).all()
    
    # Проверяем доступность заданий
    result = []
    for i, assn in enumerate(assignments):
        if i == 0:
            result.append(assn)
        else:
            prev_assn = assignments[i-1]
            prev_submission = db.query(Submission).filter(
                Submission.assignment_id == prev_assn.id,
                Submission.user_id == current_user.id
            ).first()
            if prev_submission:
                review = db.query(Review).filter(
                    Review.submission_id == prev_submission.id,
                    Review.reviewer_id == current_user.id
                ).first()
                if review:
                    result.append(assn)
                else:
                    break
            else:
                break
    
    return result

@app.post("/assignments/{assignment_id}/submit")
def submit_assignment(assignment_id: int, submission: SubmissionCreate,
                     db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Проверяем, что трек начался
    if not assignment.track.started_at:
        raise HTTPException(status_code=400, detail="Track has not started yet")
    
    deadline = assignment.track.started_at + timedelta(days=assignment.deadline_days)
    if datetime.utcnow() > deadline:
        raise HTTPException(status_code=400, detail="Deadline passed")
    
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.user_id == current_user.id
    ).first()
    if existing:
        existing.repository_url = submission.repository_url
        existing.submitted_at = datetime.utcnow()
    else:
        db_submission = Submission(
            assignment_id=assignment_id,
            user_id=current_user.id,
            repository_url=submission.repository_url
        )
        db.add(db_submission)
    
    db.commit()
    return {"message": "Submitted successfully"}

@app.get("/assignments/{assignment_id}/review")
def get_review_assignment(assignment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Проверяем, что трек начался
    if not assignment.track.started_at:
        raise HTTPException(status_code=400, detail="Track has not started yet")
    
    deadline = assignment.track.started_at + timedelta(days=assignment.deadline_days)
    if datetime.utcnow() < deadline:
        raise HTTPException(status_code=400, detail="Deadline not passed yet")
    
    # Получаем случайную работу для ревью
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.user_id != current_user.id
    ).all()
    
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions to review")
    
    # Проверяем, не ревьюил ли уже
    reviewed_ids = [r.submission_id for r in db.query(Review).filter(Review.reviewer_id == current_user.id).all()]
    available = [s for s in submissions if s.id not in reviewed_ids]
    
    if not available:
        return {"message": "All submissions reviewed"}
    
    submission = random.choice(available)
    return {
        "submission_id": submission.id,
        "repository_url": submission.repository_url,
        "submitted_at": submission.submitted_at
    }

@app.post("/submissions/{submission_id}/review")
def submit_review(submission_id: int, review: ReviewCreate,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot review own submission")
    
    existing = db.query(Review).filter(
        Review.submission_id == submission_id,
        Review.reviewer_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already reviewed")
    
    db_review = Review(
        submission_id=submission_id,
        reviewer_id=current_user.id,
        score=review.score,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    return {"message": "Review submitted"}

@app.get("/assignments/{assignment_id}/comments")
def get_comments(assignment_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    comments = db.query(Comment).filter(Comment.assignment_id == assignment_id).order_by(Comment.created_at).all()
    return [{"id": c.id, "text": c.text, "user_id": c.user_id, "created_at": c.created_at} for c in comments]

@app.post("/assignments/{assignment_id}/comments")
def create_comment(assignment_id: int, comment: CommentCreate,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = Comment(
        assignment_id=assignment_id,
        user_id=current_user.id,
        text=comment.text
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return {"id": db_comment.id, "text": db_comment.text, "user_id": db_comment.user_id,
            "created_at": db_comment.created_at}

@app.get("/notifications")
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifications = []
    
    # Получаем все треки пользователя
    tracks = db.query(Track).join(TrackParticipant).filter(
        TrackParticipant.user_id == current_user.id,
        Track.started_at.isnot(None)
    ).all()
    
    for track in tracks:
        assignments = db.query(Assignment).filter(Assignment.track_id == track.id).order_by(Assignment.order).all()
        for assn in assignments:
            # Проверяем, что трек начался (для безопасности)
            if not track.started_at:
                continue
            
            deadline = track.started_at + timedelta(days=assn.deadline_days)
            days_left = (deadline - datetime.utcnow()).days
            
            # Уведомление за 2 дня до дедлайна
            if 0 <= days_left <= 2:
                notifications.append({
                    "type": "deadline_warning",
                    "message": f"Assignment '{assn.title}' deadline in {days_left} days",
                    "assignment_id": assn.id
                })
            
            # Уведомление о начале код-ривью
            if datetime.utcnow() > deadline:
                submission = db.query(Submission).filter(
                    Submission.assignment_id == assn.id,
                    Submission.user_id == current_user.id
                ).first()
                if submission:
                    review = db.query(Review).filter(
                        Review.submission_id == submission.id,
                        Review.reviewer_id == current_user.id
                    ).first()
                    if not review:
                        notifications.append({
                            "type": "code_review",
                            "message": f"Code review started for '{assn.title}'",
                            "assignment_id": assn.id
                        })
    
    return notifications

