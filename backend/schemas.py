from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str  # email
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    class Config:
        from_attributes = True

class TrackCreate(BaseModel):
    title: str
    description: str
    quota: int
    criteria: str
    assignments: List[dict]  # [{"title": "...", "description": "...", "deadline_days": 7, "order": 1}]

class TrackResponse(BaseModel):
    id: int
    title: str
    description: str
    quota: int
    started_at: Optional[datetime]
    participant_count: int
    class Config:
        from_attributes = True

class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: str
    deadline_days: int
    order: int
    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    repository_url: str

class ReviewCreate(BaseModel):
    score: float
    comment: str

class CommentCreate(BaseModel):
    text: str

