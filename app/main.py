from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.protected import router as protected_router
from routes.bets import router as bets_router

app = FastAPI(title="Paris Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(protected_router, tags=["Users"])
app.include_router(bets_router, prefix="/bets", tags=["Bets"])

@app.get("/")
async def root():
    return {"message": "Hello from Paris Backend!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ranking")
async def get_ranking_endpoint(league: str = None):
    """
    Voir le classement global ou par ligue
    
    Nouveau système de points :
    - 1 bon pari = +10 points  
    - 1 mauvais pari = -5 points
    """
    from utils.auth import get_ranking
    ranking = get_ranking(league)
    
    return {
        "league": league or "global",
        "total_users": len(ranking),
        "users": ranking
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)