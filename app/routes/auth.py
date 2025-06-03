from fastapi import APIRouter, HTTPException
from models import UserRegister, UserLogin, LoginResponse
from utils.auth import create_user, authenticate_user, create_session_token, logout_user, get_all_users

router = APIRouter()

@router.post("/register")
async def register(user: UserRegister):
    """Créer un nouveau compte utilisateur"""
    if not create_user(user.login, user.password):
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    
    return {"message": "Utilisateur créé avec succès"}

@router.post("/login", response_model=LoginResponse)
async def login(user: UserLogin):
    """Se connecter avec login/password"""
    if not authenticate_user(user.login, user.password):
        raise HTTPException(status_code=401, detail="Login ou mot de passe incorrect")
    
    token = create_session_token(user.login)
    return LoginResponse(message="Connexion réussie", token=token)

@router.post("/logout")
async def logout(token: str):
    """Se déconnecter"""
    logout_user(token)
    return {"message": "Déconnexion réussie"}

@router.get("/users")
async def list_users():
    """Lister tous les utilisateurs (debug)"""
    return {"users": get_all_users()}
