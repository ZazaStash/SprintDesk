from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Имя должно содержать хотя бы 2 символа")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: Literal["admin", "member"]


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=2000)
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: int = Field(default=2, ge=1, le=3)
    owner_id: int | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Название должно содержать хотя бы 2 символа")
        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: Literal["todo", "in_progress", "done"] | None = None
    priority: int | None = Field(default=None, ge=1, le=3)
    owner_id: int | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value):
        if value is None:
            return value
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Название должно содержать хотя бы 2 символа")
        return value


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    status: Literal["todo", "in_progress", "done"]
    priority: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
