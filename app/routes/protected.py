from fastapi import APIRouter, HTTPException
from utils.auth import get_current_user, get_user_profile
from models import UserProfile

router = APIRouter()

@router.get("/protected")
async def protected_route(token: str):
    """Exemple d'endpoint protégé"""
    user_login = get_current_user(token)
    return {"message": f"Bonjour {user_login}, vous êtes connecté!"}

@router.get("/users/me", response_model=UserProfile)
async def get_my_profile(token: str):
    """Récupérer mon profil utilisateur"""
    user_login = get_current_user(token)
    profile = get_user_profile(user_login)
    return UserProfile(**profile)