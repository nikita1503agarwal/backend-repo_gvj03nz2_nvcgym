"""
Database Schemas for E‑Learning Platform

Each Pydantic model corresponds to a MongoDB collection.
Collection name is the lowercase of the class name.

Examples:
- User -> "user"
- Course -> "course"
- Lesson -> "lesson"
- Enrollment -> "enrollment"
- Review -> "review"
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class User(BaseModel):
    """Basic user schema"""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None, description="Public avatar URL")
    is_instructor: bool = Field(False, description="Whether the user can create courses")


class Course(BaseModel):
    """Courses collection schema"""
    title: str = Field(..., description="Course title")
    subtitle: Optional[str] = Field(None, description="Short subtitle or tagline")
    description: str = Field(..., description="Full course description")
    instructor_name: str = Field(..., description="Instructor display name")
    instructor_email: str = Field(..., description="Instructor contact email")
    price: float = Field(0.0, ge=0, description="Price in USD (0 for free)")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    language: str = Field("English", description="Course language")
    level: str = Field("Beginner", description="Skill level")


class Lesson(BaseModel):
    """Lessons collection schema"""
    course_id: str = Field(..., description="ID of the parent course (stringified ObjectId)")
    title: str = Field(..., description="Lesson title")
    content: str = Field(..., description="Lesson content (markdown or text)")
    video_url: Optional[str] = Field(None, description="Optional video URL")
    order: int = Field(0, ge=0, description="Order within the course")


class Enrollment(BaseModel):
    """Enrollments collection schema"""
    course_id: str = Field(..., description="ID of the course (stringified ObjectId)")
    user_email: str = Field(..., description="Email of the enrolled user")
    user_name: str = Field(..., description="Name of the enrolled user")
    progress: float = Field(0, ge=0, le=100, description="Completion percentage")


class Review(BaseModel):
    """Course reviews"""
    course_id: str = Field(..., description="ID of the course (stringified ObjectId)")
    user_email: str = Field(..., description="Reviewer email")
    user_name: str = Field(..., description="Reviewer name")
    rating: int = Field(..., ge=1, le=5, description="Star rating 1-5")
    comment: Optional[str] = Field(None, description="Optional review text")
