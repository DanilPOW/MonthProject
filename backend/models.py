from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    quota = Column(Integer)  # нужное кол-во участников
    criteria = Column(Text)  # JSON строка с критериями оценки
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    participants = relationship("TrackParticipant", back_populates="track")
    assignments = relationship("Assignment", back_populates="track")

class TrackParticipant(Base):
    __tablename__ = "track_participants"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    track_id = Column(Integer, ForeignKey("tracks.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    track = relationship("Track", back_populates="participants")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.id"))
    title = Column(String)
    description = Column(Text)
    deadline_days = Column(Integer)  # дней на выполнение
    order = Column(Integer)  # порядок в треке
    track = relationship("Track", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    repository_url = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    assignment = relationship("Assignment", back_populates="submissions")
    reviews = relationship("Review", back_populates="submission")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    submission = relationship("Submission", back_populates="reviews")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

