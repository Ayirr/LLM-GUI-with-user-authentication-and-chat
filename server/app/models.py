from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    created_at: datetime
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class Conversation(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime

class LLMRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None