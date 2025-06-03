from fastapi import APIRouter
from typing import Optional, List
from utils.auth import get_ranking

router = APIRouter()

@router.get("/")
async def get_ranking_endpoint(league: Optional[str] = None):
    """
    Voir le classement global ou par ligue
    
    Système de points :
    - 1 bon pari = +10 points  
    - 1 mauvais pari = -5 points
    
    Paramètres :
    - league (optionnel) : Filtrer par ligue ("football", "tennis", etc.)
    
    Exemple d'utilisation :
    - GET /ranking → Classement global
    - GET /ranking?league=football → Classement de la ligue football
    """
    ranking = get_ranking(league)
    
    return {
        "league": league or "global",
        "total_users": len(ranking),
        "users": ranking
    }