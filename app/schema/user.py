from pydantic import BaseModel,EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3,max_length=20)

class UserCreate(UserBase):
    password: str = Field(min_length=5,max_length=50)
    
    @field_validator('password')
    def validate_password(cls, value):
        if ' ' in value:
            raise ValueError("Password must not contains spaces")
        return value

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str 
    
class LogoutRequest(BaseModel):
    access_token: str
