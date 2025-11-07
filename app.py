from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import json

from database import get_db, engine, Base
from models import User, TrackEnrollment, Submission, CodeReview
from schemas import (
    UserCreate, UserResponse, Token,
    TrackResponse, TrackEnrollmentResponse,
    AssignmentWithStatus,
    SubmissionCreate, SubmissionResponse,
    CodeReviewCreate, CodeReviewResponse,
    DiaryEntryCreate, DiaryEntryResponse
)
from auth import (
    authenticate_user, create_access_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from websocket_manager import manager
import services

app = FastAPI(title="Learning Platform API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    """Создаем таблицы при запуске приложения"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Таблицы базы данных созданы/проверены")
    except Exception as e:
        print(f"⚠ Ошибка подключения к базе данных: {e}")
        print("⚠ Убедитесь, что PostgreSQL запущен и данные в .env правильные")


# ========== Аутентификация ==========

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь с таким email
    existing_user = services.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Проверяем, существует ли пользователь с таким username
    existing_user = services.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    db_user = services.create_user(db, user)
    return db_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход и получение токена доступа"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


# ========== Треки ==========

@app.get("/tracks", response_model=List[TrackResponse])
def get_tracks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список всех треков"""
    tracks = services.get_tracks(db, skip=skip, limit=limit)
    result = []
    for track in tracks:
        # Подсчитываем текущее количество участников
        enrollments = db.query(TrackEnrollment).filter(
            TrackEnrollment.track_id == track.id
        ).count()
        track_dict = {
            "id": track.id,
            "title": track.title,
            "description": track.description,
            "required_participants": track.required_participants,
            "status": track.status,
            "started_at": track.started_at,
            "created_at": track.created_at,
            "current_participants": enrollments,
            "review_criteria": json.loads(track.review_criteria),
            "reviews_per_user": track.reviews_per_user
        }
        result.append(TrackResponse(**track_dict))
    return result


@app.get("/tracks/my", response_model=List[TrackResponse])
def get_my_tracks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить треки, на которые записан текущий пользователь"""
    tracks = services.get_user_tracks(db, current_user.id)
    result = []
    for track in tracks:
        enrollments = db.query(TrackEnrollment).filter(
            TrackEnrollment.track_id == track.id
        ).count()
        track_dict = {
            "id": track.id,
            "title": track.title,
            "description": track.description,
            "required_participants": track.required_participants,
            "status": track.status,
            "started_at": track.started_at,
            "created_at": track.created_at,
            "current_participants": enrollments,
            "review_criteria": json.loads(track.review_criteria),
            "reviews_per_user": track.reviews_per_user
        }
        result.append(TrackResponse(**track_dict))
    return result


@app.get("/tracks/{track_id}", response_model=TrackResponse)
def get_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о треке"""
    track = services.get_track(db, track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    enrollments = db.query(TrackEnrollment).filter(
        TrackEnrollment.track_id == track_id
    ).count()
    track_dict = {
        "id": track.id,
        "title": track.title,
        "description": track.description,
        "required_participants": track.required_participants,
        "status": track.status,
        "started_at": track.started_at,
        "created_at": track.created_at,
        "current_participants": enrollments,
        "review_criteria": json.loads(track.review_criteria),
        "reviews_per_user": track.reviews_per_user
    }
    return TrackResponse(**track_dict)


@app.post("/tracks/{track_id}/enroll", response_model=TrackEnrollmentResponse)
def enroll_in_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Записаться на трек"""
    try:
        enrollment = services.enroll_in_track(db, current_user.id, track_id)
        return enrollment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.delete("/tracks/{track_id}/enroll")
def unenroll_from_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Выйти из трека (только если трек еще не начался)"""
    try:
        success = services.unenroll_from_track(db, current_user.id, track_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        return {"message": "Successfully unenrolled from track"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ========== Задания ==========

@app.get("/tracks/{track_id}/assignments", response_model=List[AssignmentWithStatus])
def get_track_assignments(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список заданий трека с их статусами"""
    assignments = services.get_track_assignments(db, track_id, current_user.id)
    if not assignments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found or user not enrolled"
        )
    
    result = []
    for assignment in assignments:
        # Проверяем статус задания для текущего пользователя
        submission = db.query(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.assignment_id == assignment.id
        ).first()
        
        # Получаем трек для проверки количества ревью
        track = services.get_track(db, assignment.track_id)
        reviews_count = 0
        if submission:
            reviews_count = services.get_reviews_count_for_assignment(
                db, current_user.id, assignment.id
            )
        
        # Определяем текущий этап
        if not submission:
            current_stage = "submission"
            is_available = True
            submission_deadline = None
            code_review_deadline = None
        elif submission and reviews_count < track.reviews_per_user:
            current_stage = "code_review"
            is_available = True
            from datetime import timedelta
            submission_deadline = submission.submitted_at + timedelta(hours=assignment.deadline_hours)
            code_review_deadline = submission_deadline
        else:
            current_stage = "completed"
            is_available = False
            submission_deadline = None
            code_review_deadline = None
        
        assignment_dict = {
            "id": assignment.id,
            "track_id": assignment.track_id,
            "title": assignment.title,
            "description": assignment.description,
            "order": assignment.order,
            "deadline_hours": assignment.deadline_hours,
            "created_at": assignment.created_at,
            "is_available": is_available,
            "submission_deadline": submission_deadline,
            "code_review_deadline": code_review_deadline,
            "current_stage": current_stage
        }
        result.append(AssignmentWithStatus(**assignment_dict))
    
    return result


@app.get("/tracks/{track_id}/assignments/current", response_model=AssignmentWithStatus)
def get_current_assignment(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить текущее доступное задание для пользователя"""
    assignment = services.get_current_assignment_for_user(db, track_id, current_user.id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available assignment found"
        )
    
    # Получаем статус задания
    submission = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.assignment_id == assignment.id
    ).first()
    
    code_review = None
    if submission:
        code_review = db.query(CodeReview).filter(
            CodeReview.submission_id == submission.id
        ).first()
    
    # Получаем трек для проверки количества ревью
    track = services.get_track(db, assignment.track_id)
    reviews_count = 0
    if submission:
        reviews_count = services.get_reviews_count_for_assignment(
            db, current_user.id, assignment.id
        )
    
    if not submission:
        current_stage = "submission"
        is_available = True
        submission_deadline = None
        code_review_deadline = None
    elif submission and reviews_count < track.reviews_per_user:
        current_stage = "code_review"
        is_available = True
        from datetime import timedelta
        submission_deadline = submission.submitted_at + timedelta(hours=assignment.deadline_hours)
        code_review_deadline = submission_deadline
    else:
        current_stage = "completed"
        is_available = False
        submission_deadline = None
        code_review_deadline = None
    
    assignment_dict = {
        "id": assignment.id,
        "track_id": assignment.track_id,
        "title": assignment.title,
        "description": assignment.description,
        "order": assignment.order,
        "deadline_hours": assignment.deadline_hours,
        "created_at": assignment.created_at,
        "is_available": is_available,
        "submission_deadline": submission_deadline,
        "code_review_deadline": code_review_deadline,
        "current_stage": current_stage
    }
    return AssignmentWithStatus(**assignment_dict)


@app.post("/assignments/{assignment_id}/submit", response_model=SubmissionResponse)
def submit_assignment(
    assignment_id: int,
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправить решение на задание"""
    try:
        db_submission = services.submit_assignment(
            db, current_user.id, assignment_id, submission
        )
        return db_submission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ========== Код-ривью ==========

@app.get("/assignments/{assignment_id}/review/submission", response_model=SubmissionResponse)
def get_submission_for_review(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить случайное submission для код-ривью"""
    try:
        submission = services.get_submission_for_review(
            db, current_user.id, assignment_id
        )
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No submission available for review"
            )
        return submission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/submissions/{submission_id}/review", response_model=CodeReviewResponse)
def create_code_review(
    submission_id: int,
    review: CodeReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать код-ривью для submission"""
    try:
        db_review = services.create_code_review(
            db, current_user.id, submission_id, review
        )
        # Преобразуем criteria_scores из JSON строки в dict
        review_dict = {
            "id": db_review.id,
            "submission_id": db_review.submission_id,
            "reviewer_id": db_review.reviewer_id,
            "reviewee_id": db_review.reviewee_id,
            "criteria_scores": json.loads(db_review.criteria_scores),
            "comment": db_review.comment,
            "completed_at": db_review.completed_at
        }
        return CodeReviewResponse(**review_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ========== Дневник ==========

@app.post("/assignments/{assignment_id}/diary", response_model=DiaryEntryResponse)
def create_diary_entry(
    assignment_id: int,
    entry: DiaryEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать запись в дневнике под заданием"""
    try:
        db_entry = services.create_diary_entry(
            db, current_user.id, assignment_id, entry
        )
        # Добавляем username к ответу
        entry_dict = {
            "id": db_entry.id,
            "user_id": db_entry.user_id,
            "assignment_id": db_entry.assignment_id,
            "content": db_entry.content,
            "created_at": db_entry.created_at,
            "username": current_user.username
        }
        return DiaryEntryResponse(**entry_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/assignments/{assignment_id}/diary", response_model=List[DiaryEntryResponse])
def get_diary_entries(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все записи дневника для задания"""
    entries = services.get_diary_entries(db, assignment_id)
    result = []
    for entry in entries:
        user = db.query(User).filter(User.id == entry.user_id).first()
        entry_dict = {
            "id": entry.id,
            "user_id": entry.user_id,
            "assignment_id": entry.assignment_id,
            "content": entry.content,
            "created_at": entry.created_at,
            "username": user.username if user else "Unknown"
        }
        result.append(DiaryEntryResponse(**entry_dict))
    return result


# ========== WebSocket для уведомлений ==========

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket эндпоинт для получения уведомлений"""
    # Проверяем токен и получаем пользователя
    from jose import jwt
    from auth import SECRET_KEY, ALGORITHM
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            await websocket.close(code=1008)
            return
        
        # Получаем пользователя из БД
        db = next(get_db())
        user = services.get_user_by_username(db, username)
        if not user:
            await websocket.close(code=1008)
            return
        
        # Подключаем пользователя
        await manager.connect(websocket, user.id)
        
        try:
            while True:
                # Ждем сообщения от клиента (ping/pong)
                data = await websocket.receive_text()
                # Можно добавить обработку сообщений от клиента
        except WebSocketDisconnect:
            manager.disconnect(user.id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


# ========== Утилиты ==========

@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

