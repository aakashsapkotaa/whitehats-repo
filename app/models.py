from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth Models ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    college: str = ""
    branch: str = ""
    semester: int = 1


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- Community Models ---
class CommentCreate(BaseModel):
    text: str


class ReportCreate(BaseModel):
    reason: str = "Inappropriate content"


# --- Group Models ---
class GroupCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "General"


class GroupPostCreate(BaseModel):
    text: str