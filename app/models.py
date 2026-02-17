from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# --- Auth ---
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    college: str
    branch: str
    semester: int

class UserLogin(BaseModel):
    email: str
    password: str

# --- Resources ---
class ResourceCreate(BaseModel):
    title: str
    subject: str
    semester: int
    resource_type: str  # notes, pdf, slides, paper, etc.
    year: Optional[int] = None
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    privacy: str = "public"  # "public" or "private"

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    semester: Optional[int] = None
    resource_type: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy: Optional[str] = None

# --- Reviews ---
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = ""
