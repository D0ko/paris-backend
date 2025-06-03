from fastapi import APIRouter, HTTPException
from typing import List, Optional
from utils.auth import (
    get_current_user, create_bet, get_all_bets, get_bet_detail, 
    vote_on_bet, resolve_bet, get_ranking
)
from models import (
    BetCreate, BetResponse, BetDetail, VoteCreate, BetResolve, RankingResponse
)

router = APIRouter()

@router.get("/", response_model=List[BetResponse])
async def list_bets():
    """Obtenir la liste de tous les paris"""
    bets = get_all_bets()
    return [BetResponse(**bet) for bet in bets]

@router.post("/", response_model=dict)
async def create_new_bet(bet: BetCreate, token: str):
    """Créer un nouveau pari"""
    user_login = get_current_user(token)
    
    if len(bet.options) < 2:
        raise HTTPException(status_code=400, detail="Il faut au moins 2 options")
    
    bet_id = create_bet(
        title=bet.title,
        description=bet.description,
        options=bet.options,
        creator=user_login,
        league=bet.league
    )
    
    return {"message": "Pari créé avec succès", "bet_id": bet_id}

@router.get("/{bet_id}", response_model=BetDetail)
async def get_bet_details(bet_id: str):
    """Voir les détails d'un pari"""
    bet = get_bet_detail(bet_id)
    if not bet:
        raise HTTPException(status_code=404, detail="Pari non trouvé")
    
    return BetDetail(**bet)

@router.post("/{bet_id}/vote")
async def vote_bet(bet_id: str, vote: VoteCreate, token: str):
    """Voter sur un pari"""
    user_login = get_current_user(token)
    
    success = vote_on_bet(bet_id, user_login, vote.option_index)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de voter (pari inexistant, déjà voté, ou option invalide)"
        )
    
    return {"message": "Vote enregistré avec succès"}

@router.post("/{bet_id}/resolve")
async def resolve_bet_endpoint(bet_id: str, resolution: BetResolve, token: str):
    """Clôturer un pari et déclarer la bonne réponse"""
    user_login = get_current_user(token)
    
    success = resolve_bet(bet_id, resolution.winning_option_index, user_login)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Impossible de résoudre le pari (inexistant, déjà résolu, ou pas autorisé)"
        )
    
    return {"message": "Pari résolu avec succès"}