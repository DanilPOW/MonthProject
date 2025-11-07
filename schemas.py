from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List, Dict


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be no longer than 72 bytes')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Track schemas
class TrackCreate(BaseModel):
    title: str
    description: Optional[str] = None
    required_participants: int
    review_criteria: Dict[str, str]  # {"criterion1": "Описание критерия 1", ...}
    reviews_per_user: int = 3  # Количество ревью, которые должен сделать каждый


class TrackResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    required_participants: int
    status: str
    started_at: Optional[datetime]
    created_at: datetime
    current_participants: int
    review_criteria: Dict[str, str]
    reviews_per_user: int

    class Config:
        from_attributes = True


class TrackEnrollmentResponse(BaseModel):
    id: int
    user_id: int
    track_id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True


# Assignment schemas
class AssignmentCreate(BaseModel):
    title: str
    description: str
    order: int
    deadline_hours: int


class AssignmentResponse(BaseModel):
    id: int
    track_id: int
    title: str
    description: str
    order: int
    deadline_hours: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentWithStatus(BaseModel):
    id: int
    track_id: int
    title: str
    description: str
    order: int
    deadline_hours: int
    created_at: datetime
    is_available: bool
    submission_deadline: Optional[datetime]
    code_review_deadline: Optional[datetime]
    current_stage: str  # "not_started", "submission", "code_review", "completed"

    class Config:
        from_attributes = True


# Submission schemas
class SubmissionCreate(BaseModel):
    repository_url: str


class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    assignment_id: int
    repository_url: str
    submitted_at: datetime

    class Config:
        from_attributes = True


# Code Review schemas
class CodeReviewCreate(BaseModel):
    criteria_scores: Dict[str, float]  # {"criterion1": 5.0, "criterion2": 4.0}
    comment: Optional[str] = None


class CodeReviewResponse(BaseModel):
    id: int
    submission_id: int
    reviewer_id: int
    reviewee_id: int
    criteria_scores: Dict[str, float]
    comment: Optional[str]
    completed_at: datetime

    class Config:
        from_attributes = True


# Diary schemas
class DiaryEntryCreate(BaseModel):
    content: str


class DiaryEntryResponse(BaseModel):
    id: int
    user_id: int
    assignment_id: int
    content: str
    created_at: datetime
    username: str

    class Config:
        from_attributes = True

