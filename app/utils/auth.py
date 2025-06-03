from passlib.context import CryptContext
import secrets
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, List
import uuid

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bases de données simples en mémoire
users_db = {}
sessions = {}
bets_db = {}  # {bet_id: bet_data}
votes_db = {}  # {bet_id: [votes]}
user_stats = {}  # {login: {points, total_bets, won_bets, etc.}}

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
    
    # Initialiser les stats de l'utilisateur
    user_stats[login] = {
        "points": 0,
        "total_bets": 0,
        "won_bets": 0,
        "lost_bets": 0
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

def get_user_profile(login: str) -> dict:
    """Récupère le profil d'un utilisateur"""
    if login not in user_stats:
        user_stats[login] = {"points": 0, "total_bets": 0, "won_bets": 0, "lost_bets": 0}
    
    stats = user_stats[login]
    return {
        "login": login,
        "total_bets": stats["total_bets"],
        "won_bets": stats["won_bets"],
        "lost_bets": stats["lost_bets"],
        "points": stats["points"]
    }

def create_bet(title: str, description: str, options: List[str], creator: str, league: str = "general") -> str:
    """Crée un nouveau pari"""
    bet_id = str(uuid.uuid4())
    
    bets_db[bet_id] = {
        "id": bet_id,
        "title": title,
        "description": description,
        "options": options,
        "status": "active",
        "creator": creator,
        "league": league,
        "created_at": datetime.now(),
        "resolved_option": None
    }
    
    votes_db[bet_id] = []
    return bet_id

def get_all_bets() -> List[dict]:
    """Récupère tous les paris"""
    result = []
    for bet_id, bet in bets_db.items():
        total_votes = len(votes_db.get(bet_id, []))
        result.append({
            **bet,
            "total_votes": total_votes
        })
    return result

def get_bet_detail(bet_id: str) -> dict:
    """Récupère les détails d'un pari"""
    if bet_id not in bets_db:
        return None
    
    bet = bets_db[bet_id]
    votes = votes_db.get(bet_id, [])
    
    # Compter les votes par option
    vote_counts = {}
    for vote in votes:
        option_idx = vote["option_index"]
        vote_counts[option_idx] = vote_counts.get(option_idx, 0) + 1
    
    return {
        **bet,
        "votes": votes,
        "vote_counts": vote_counts
    }

def vote_on_bet(bet_id: str, user: str, option_index: int) -> bool:
    """Vote sur un pari"""
    if bet_id not in bets_db:
        return False
    
    bet = bets_db[bet_id]
    if bet["status"] != "active":
        return False
    
    if option_index < 0 or option_index >= len(bet["options"]):
        return False
    
    # Vérifier si l'utilisateur a déjà voté
    votes = votes_db.get(bet_id, [])
    for vote in votes:
        if vote["user"] == user:
            return False  # Déjà voté
    
    # Ajouter le vote
    vote = {
        "user": user,
        "option_index": option_index,
        "voted_at": datetime.now()
    }
    votes_db[bet_id].append(vote)
    
    # Mettre à jour les stats de l'utilisateur
    if user not in user_stats:
        user_stats[user] = {"points": 0, "total_bets": 0, "won_bets": 0, "lost_bets": 0}
    user_stats[user]["total_bets"] += 1
    
    return True

def resolve_bet(bet_id: str, winning_option_index: int, resolver: str) -> bool:
    """Résout un pari et distribue les points"""
    if bet_id not in bets_db:
        return False
    
    bet = bets_db[bet_id]
    if bet["status"] != "active":
        return False
    
    # Seul le créateur peut résoudre le pari
    if bet["creator"] != resolver:
        return False
    
    if winning_option_index < 0 or winning_option_index >= len(bet["options"]):
        return False
    
    # Marquer le pari comme résolu
    bets_db[bet_id]["status"] = "resolved"
    bets_db[bet_id]["resolved_option"] = winning_option_index
    
    # Distribuer les points selon le nouveau système
    votes = votes_db.get(bet_id, [])
    winners = [vote for vote in votes if vote["option_index"] == winning_option_index]
    losers = [vote for vote in votes if vote["option_index"] != winning_option_index]
    
    # Nouveau système de points : +10 pour les gagnants, -5 pour les perdants
    for winner_vote in winners:
        user = winner_vote["user"]
        if user not in user_stats:
            user_stats[user] = {"points": 0, "total_bets": 0, "won_bets": 0, "lost_bets": 0}
        user_stats[user]["points"] += 10  # +10 points pour un bon pari
        user_stats[user]["won_bets"] += 1
    
    for loser_vote in losers:
        user = loser_vote["user"]
        if user not in user_stats:
            user_stats[user] = {"points": 0, "total_bets": 0, "won_bets": 0, "lost_bets": 0}
        user_stats[user]["points"] -= 5   # -5 points pour un mauvais pari
        user_stats[user]["lost_bets"] += 1
    
    return True

def get_ranking(league: str = None) -> List[dict]:
    """Récupère le classement"""
    ranking = []
    
    for login, stats in user_stats.items():
        if stats["total_bets"] > 0:
            win_rate = stats["won_bets"] / stats["total_bets"]
        else:
            win_rate = 0.0
        
        ranking.append({
            "login": login,
            "points": stats["points"],
            "total_bets": stats["total_bets"],
            "won_bets": stats["won_bets"],
            "win_rate": round(win_rate, 2)
        })
    
    # Trier par points puis par taux de réussite
    ranking.sort(key=lambda x: (x["points"], x["win_rate"]), reverse=True)
    
    return ranking