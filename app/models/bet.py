from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class BetStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class BetCreate(BaseModel):
    title: str
    description: str
    options: List[str]  # Liste des choix possibles
    league: Optional[str] = "general"
    
class BetResponse(BaseModel):
    id: str
    title: str
    description: str
    options: List[str]
    status: BetStatus
    creator: str
    league: str
    created_at: datetime
    total_votes: int

class VoteCreate(BaseModel):
    option_index: int  # Index de l'option choisie

class Vote(BaseModel):
    user: str
    option_index: int
    voted_at: datetime

class BetDetail(BaseModel):
    id: str
    title: str
    description: str
    options: List[str]
    status: BetStatus
    creator: str
    league: str
    created_at: datetime
    votes: List[Vote]
    vote_counts: Dict[int, int]  # {option_index: count}
    resolved_option: Optional[int] = None

class BetResolve(BaseModel):
    winning_option_index: int

class RankingUser(BaseModel):
    login: str
    points: int
    total_bets: int
    won_bets: int
    win_rate: float

class RankingResponse(BaseModel):
    league: str
    users: List[RankingUser]