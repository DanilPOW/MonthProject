from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import (
    User, Track, TrackEnrollment, Assignment, Submission,
    CodeReview, DiaryEntry
)
from schemas import (
    UserCreate, TrackCreate, SubmissionCreate,
    CodeReviewCreate, DiaryEntryCreate
)
from auth import get_password_hash
import json
import random


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_tracks(db: Session, skip: int = 0, limit: int = 100) -> List[Track]:
    tracks = db.query(Track).offset(skip).limit(limit).all()
    return tracks


def get_track(db: Session, track_id: int) -> Optional[Track]:
    return db.query(Track).filter(Track.id == track_id).first()


def create_track(db: Session, track: TrackCreate) -> Track:
    db_track = Track(
        title=track.title,
        description=track.description,
        required_participants=track.required_participants,
        review_criteria=json.dumps(track.review_criteria),
        reviews_per_user=track.reviews_per_user
    )
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return db_track


def enroll_in_track(db: Session, user_id: int, track_id: int) -> TrackEnrollment:
    # Проверяем, не записан ли уже пользователь
    existing = db.query(TrackEnrollment).filter(
        and_(
            TrackEnrollment.user_id == user_id,
            TrackEnrollment.track_id == track_id
        )
    ).first()
    if existing:
        raise ValueError("User already enrolled in this track")

    # Проверяем, не начался ли трек
    track = get_track(db, track_id)
    if track.status != "waiting":
        raise ValueError("Track has already started")

    enrollment = TrackEnrollment(user_id=user_id, track_id=track_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    # Проверяем, достигнуто ли необходимое количество участников
    participants_count = db.query(TrackEnrollment).filter(
        TrackEnrollment.track_id == track_id
    ).count()

    if participants_count >= track.required_participants:
        track.status = "active"
        track.started_at = datetime.utcnow()
        db.commit()

    return enrollment


def unenroll_from_track(db: Session, user_id: int, track_id: int) -> bool:
    track = get_track(db, track_id)
    if track.status != "waiting":
        raise ValueError("Cannot unenroll from active or completed track")

    enrollment = db.query(TrackEnrollment).filter(
        and_(
            TrackEnrollment.user_id == user_id,
            TrackEnrollment.track_id == track_id
        )
    ).first()

    if not enrollment:
        return False

    db.delete(enrollment)
    db.commit()
    return True


def get_user_tracks(db: Session, user_id: int) -> List[Track]:
    enrollments = db.query(TrackEnrollment).filter(
        TrackEnrollment.user_id == user_id
    ).all()
    track_ids = [e.track_id for e in enrollments]
    if not track_ids:
        return []
    tracks = db.query(Track).filter(Track.id.in_(track_ids)).all()
    return tracks


def get_track_assignments(db: Session, track_id: int, user_id: int) -> List[Assignment]:
    track = get_track(db, track_id)
    if not track:
        return []

    # Проверяем, что пользователь записан на трек
    enrollment = db.query(TrackEnrollment).filter(
        and_(
            TrackEnrollment.user_id == user_id,
            TrackEnrollment.track_id == track_id
        )
    ).first()
    if not enrollment:
        return []

    assignments = db.query(Assignment).filter(
        Assignment.track_id == track_id
    ).order_by(Assignment.order).all()

    return assignments


def get_current_assignment_for_user(
    db: Session, track_id: int, user_id: int
) -> Optional[Assignment]:
    assignments = get_track_assignments(db, track_id, user_id)
    if not assignments:
        return None

    track = get_track(db, track_id)
    if not track:
        return None

    # Находим первое задание, которое еще не завершено пользователем
    for i, assignment in enumerate(assignments):
        # Проверяем предыдущее задание (если есть)
        if i > 0:
            prev_assignment = assignments[i - 1]
            prev_submission = db.query(Submission).filter(
                and_(
                    Submission.user_id == user_id,
                    Submission.assignment_id == prev_assignment.id
                )
            ).first()

            # Если предыдущее задание не завершено, не даем доступ к текущему
            if not prev_submission:
                return prev_assignment

            # Проверяем, завершено ли код-ривью для предыдущего задания
            # Пользователь должен сделать reviews_per_user ревью
            reviews_count = get_reviews_count_for_assignment(
                db, user_id, prev_assignment.id
            )
            if reviews_count < track.reviews_per_user:
                return prev_assignment

        # Проверяем текущее задание
        submission = db.query(Submission).filter(
            and_(
                Submission.user_id == user_id,
                Submission.assignment_id == assignment.id
            )
        ).first()

        if not submission:
            return assignment

        # Проверяем, завершено ли код-ривью для этого задания
        reviews_count = get_reviews_count_for_assignment(
            db, user_id, assignment.id
        )
        if reviews_count < track.reviews_per_user:
            return assignment  # На этапе код-ривью

    # Все задания завершены
    return None


def submit_assignment(db: Session, user_id: int, assignment_id: int, submission: SubmissionCreate) -> Submission:
    # Проверяем, что задание доступно
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise ValueError("Assignment not found")

    # Проверяем, что пользователь записан на трек
    enrollment = db.query(TrackEnrollment).filter(
        and_(
            TrackEnrollment.user_id == user_id,
            TrackEnrollment.track_id == assignment.track_id
        )
    ).first()
    if not enrollment:
        raise ValueError("User not enrolled in this track")

    # Проверяем, что трек начался
    track = get_track(db, assignment.track_id)
    if track.status != "active":
        raise ValueError("Track is not active")

    # Проверяем, не отправлено ли уже решение
    existing = db.query(Submission).filter(
        and_(
            Submission.user_id == user_id,
            Submission.assignment_id == assignment_id
        )
    ).first()
    if existing:
        raise ValueError("Submission already exists")

    db_submission = Submission(
        user_id=user_id,
        assignment_id=assignment_id,
        repository_url=submission.repository_url
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


def get_reviews_count_for_assignment(
    db: Session, reviewer_id: int, assignment_id: int
) -> int:
    """Получить количество завершенных ревью для задания"""
    return db.query(CodeReview).filter(
        and_(
            CodeReview.reviewer_id == reviewer_id,
            CodeReview.submission_id.in_(
                db.query(Submission.id).filter(
                    Submission.assignment_id == assignment_id
                )
            )
        )
    ).count()


def get_submission_for_review(
    db: Session, reviewer_id: int, assignment_id: int
) -> Optional[Submission]:
    # Получаем трек и задание для проверки количества ревью
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    if not assignment:
        return None

    track = get_track(db, assignment.track_id)
    if not track:
        return None

    # Проверяем, сколько ревью уже сделал пользователь
    reviews_count = get_reviews_count_for_assignment(
        db, reviewer_id, assignment_id
    )
    if reviews_count >= track.reviews_per_user:
        raise ValueError(
            f"Already completed {reviews_count} reviews. "
            f"Required: {track.reviews_per_user}"
        )

    # Получаем все submission для этого задания
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()

    if not submissions:
        return None

    # Исключаем submission, которые уже были оценены этим ревьюером
    reviewed_submission_ids = db.query(CodeReview.submission_id).filter(
        CodeReview.reviewer_id == reviewer_id
    ).all()
    reviewed_ids = [r[0] for r in reviewed_submission_ids]

    available_submissions = [
        s for s in submissions
        if s.id not in reviewed_ids and s.user_id != reviewer_id
    ]

    if not available_submissions:
        return None

    # Возвращаем случайное submission
    return random.choice(available_submissions)


def create_code_review(db: Session, reviewer_id: int, submission_id: int, review: CodeReviewCreate) -> CodeReview:
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise ValueError("Submission not found")

    # Проверяем, что ревьюер не оценивает свое собственное решение
    if submission.user_id == reviewer_id:
        raise ValueError("Cannot review own submission")

    # Проверяем, что ревьюер еще не оценивал это submission
    existing = db.query(CodeReview).filter(
        and_(
            CodeReview.reviewer_id == reviewer_id,
            CodeReview.submission_id == submission_id
        )
    ).first()
    if existing:
        raise ValueError("Review already exists")

    db_review = CodeReview(
        submission_id=submission_id,
        reviewer_id=reviewer_id,
        reviewee_id=submission.user_id,
        criteria_scores=json.dumps(review.criteria_scores),
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def create_diary_entry(db: Session, user_id: int, assignment_id: int, entry: DiaryEntryCreate) -> DiaryEntry:
    # Проверяем, что пользователь записан на трек с этим заданием
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise ValueError("Assignment not found")

    enrollment = db.query(TrackEnrollment).filter(
        and_(
            TrackEnrollment.user_id == user_id,
            TrackEnrollment.track_id == assignment.track_id
        )
    ).first()
    if not enrollment:
        raise ValueError("User not enrolled in this track")

    db_entry = DiaryEntry(
        user_id=user_id,
        assignment_id=assignment_id,
        content=entry.content
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_diary_entries(db: Session, assignment_id: int) -> List[DiaryEntry]:
    entries = db.query(DiaryEntry).filter(
        DiaryEntry.assignment_id == assignment_id
    ).order_by(DiaryEntry.created_at.desc()).all()
    return entries


def check_deadline_notifications(db: Session):
    """Проверяет дедлайны и отправляет уведомления при 80% времени"""
    from datetime import timedelta

    # Получаем все активные submission
    submissions = db.query(Submission).filter(
        Submission.deadline_notification_sent.is_(False)
    ).all()

    for submission in submissions:
        assignment = db.query(Assignment).filter(
            Assignment.id == submission.assignment_id
        ).first()

        if not assignment:
            continue

        # Вычисляем время уведомления (80% от дедлайна)
        notification_time = submission.submitted_at + timedelta(
            hours=assignment.deadline_hours * 0.8
        )

        # Если прошло 80% времени, отправляем уведомление
        if datetime.utcnow() >= notification_time:
            submission.deadline_notification_sent = True
            db.commit()
            # Здесь можно добавить отправку email/WebSocket уведомления
            # send_notification(submission.user_id, "Deadline approaching")

