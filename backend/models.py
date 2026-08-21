from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

Role = Literal['super_admin', 'admin', 'manager']


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class LoginOut(BaseModel):
    access_token: str
    user: 'UserOut'


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: Role
    created_at: str
    last_login_at: Optional[str] = None
    disabled: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    role: Role
    password: str = Field(min_length=10, max_length=200)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    role: Optional[Role] = None
    disabled: Optional[bool] = None


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=10, max_length=200)


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=10, max_length=200)


LoginOut.model_rebuild()
