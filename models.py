from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    track_enrollments = relationship("TrackEnrollment", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    code_reviews_given = relationship("CodeReview", foreign_keys="CodeReview.reviewer_id", back_populates="reviewer")
    code_reviews_received = relationship("CodeReview", foreign_keys="CodeReview.reviewee_id", back_populates="reviewee")
    diary_entries = relationship("DiaryEntry", back_populates="user")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    required_participants = Column(Integer, nullable=False)
    status = Column(String, default="waiting")  # waiting, active, completed
    started_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    review_criteria = Column(Text, nullable=False)  # JSON строка с критериями код-ривью
    reviews_per_user = Column(Integer, default=3)  # Количество ревью, которые должен сделать каждый

    # Relationships
    enrollments = relationship("TrackEnrollment", back_populates="track")
    assignments = relationship("Assignment", back_populates="track", order_by="Assignment.order")


class TrackEnrollment(Base):
    __tablename__ = "track_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="track_enrollments")
    track = relationship("Track", back_populates="enrollments")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)  # Порядок задания в треке
    deadline_hours = Column(Integer, nullable=False)  # Количество часов на выполнение
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    track = relationship("Track", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
    diary_entries = relationship("DiaryEntry", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    repository_url = Column(String, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline_notification_sent = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
    code_reviews = relationship("CodeReview", back_populates="submission")


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criteria_scores = Column(Text)  # JSON строка с оценками по критериям
    comment = Column(Text)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    submission = relationship("Submission", back_populates="code_reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="code_reviews_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="code_reviews_received")


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="diary_entries")
    assignment = relationship("Assignment", back_populates="diary_entries")

