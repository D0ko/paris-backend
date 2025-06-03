from fastapi import APIRouter
from utils.auth import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_route(token: str):
    """Exemple d'endpoint protégé"""
    user_login = get_current_user(token)
    return {"message": f"Bonjour {user_login}, vous êtes connecté!"}

# Ajoutez vos autres endpoints protégés ici
@router.get("/profile")
async def get_profile(token: str):
    """Récupérer le profil utilisateur"""
    user_login = get_current_user(token)
    return {"login": user_login, "message": "Voici votre profil"}
