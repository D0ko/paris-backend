from passlib.context import CryptContext
import secrets
from fastapi import HTTPException

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bases de données simples en mémoire
users_db = {}
sessions = {}

def hash_password(password: str) -> str:
    """Hash un mot de passe"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un mot de passe contre son hash"""
    return pwd_context.verify(password, hashed)

def create_session_token(login: str) -> str:
    """Crée un token de session pour un utilisateur"""
    token = secrets.token_urlsafe(32)
    sessions[token] = login
    return token

def get_current_user(token: str = None) -> str:
    """Récupère l'utilisateur actuel à partir du token"""
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Non autorisé")
    return sessions[token]

def create_user(login: str, password: str) -> bool:
    """Crée un nouvel utilisateur"""
    if login in users_db:
        return False
    
    users_db[login] = {
        "login": login,
        "password": hash_password(password)
    }
    return True

def authenticate_user(login: str, password: str) -> bool:
    """Authentifie un utilisateur"""
    if login not in users_db:
        return False
    
    stored_user = users_db[login]
    return verify_password(password, stored_user["password"])

def logout_user(token: str) -> bool:
    """Déconnecte un utilisateur"""
    if token in sessions:
        del sessions[token]
        return True
    return False

def get_all_users() -> list:
    """Retourne la liste des utilisateurs (pour debug)"""
    return list(users_db.keys())
