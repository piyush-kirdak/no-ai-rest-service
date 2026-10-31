
from pydantic import BaseModel, Field, EmailStr


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = ""


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None = None


# User registration schema
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# User response schema
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str