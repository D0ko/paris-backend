from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    login: str
    password: str

class UserLogin(BaseModel):
    login: str
    password: str

class LoginResponse(BaseModel):
    message: str
    token: str

class User(BaseModel):
    login: str
    password: str  # Sera hashé

class UserProfile(BaseModel):
    login: str
    total_bets: int
    won_bets: int
    lost_bets: int
    points: int
    rank: Optional[int] = None