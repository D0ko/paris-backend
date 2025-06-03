from pydantic import BaseModel

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
