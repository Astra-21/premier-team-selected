import logging, requests, os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.core.security import create_access_token, get_current_user
from app.database import get_db
from app.models import Team, Player, User
from app import models

load_dotenv()

API_TOKEN = os.getenv("YOUR_API_KEY")
HEADERS = {"X-Auth-Token": API_TOKEN}
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
client_id = "660638373406-9h904j2eq11m12edst37q185lm0j7it2.apps.googleusercontent.com"

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LoginRequest(BaseModel):
    google_id: str

class TokenData(BaseModel):
    google_id: Optional[str] = None

class FavoriteUpdateRequest(BaseModel):
    favorite_team: str
    favorite_player: str
    username: str  

class UpdateUsernameRequest(BaseModel):
    username: str

user_data_store = {}

@router.post("/login")
async def login(login_request: LoginRequest):

    id_token_str = login_request.google_id
    logging.debug(f"Received login request with google_id: {id_token_str}")
    
    #client_idはセキュリティ的に「トークンの発行先を制限」
    try:
        idinfo = id_token.verify_token(
            id_token_str,
            grequests.Request(),
            client_id
        )
        
        #issはトークンの発行元。Google が発行したことを確認
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(status_code=400, detail="Invalid issuer.")
        
    
        user_id = idinfo['sub']
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:

        logging.error(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/user/me")
async def get_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(google_id=current_user.google_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    return {
        "username": user.username,
        "favorite_team": user.favorite_team,
        "favorite_player": user.favorite_player,
        "logo_url": user.logo_url
    }

@router.post("/api/user/favorite")
async def set_favorite_team(
    request: FavoriteUpdateRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter_by(google_id=current_user.google_id).first()
    if not user:
        user = models.User(google_id=current_user.google_id, 
                           favorite_team=request.favorite_team, 
                           favorite_player=request.favorite_player, 
                           username=request.username
                           )
        db.add(user)
    else:
        user.favorite_team = request.favorite_team
        user.favorite_player = request.favorite_player
        user.username=request.username  
    db.commit()
    
    return {"status": "ok"}
   
@router.get("/api/teams")
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [{"id": t.id, "name": t.name, "logo_url": t.logo_url} for t in teams]

@router.get("/api/teams/{team_id}/players")
def get_players_by_team(team_id: int, db: Session = Depends(get_db)):
    players = db.query(Player).filter(Player.team_id == team_id).all()
    return [{"id": p.id, "name": p.name, "position": p.position} for p in players]

@router.post("/api/user/username")
async def update_username(
    request: UpdateUsernameRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter_by(google_id=current_user.google_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")
    user.username = request.username
    db.commit()
    return {"status": "ok"}

@router.get("/api/team/{team_id}/latest-match")
def get_latest_match(team_id: int):
    url = f"https://api.football-data.org/v4/teams/{team_id}/matches?status=FINISHED&limit=1"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    match = res.json()["matches"][0]

    return {
        "utcDate": match["utcDate"],
        "homeTeam": match["homeTeam"]["name"],
        "awayTeam": match["awayTeam"]["name"],
        "homeScore": match["score"]["fullTime"]["home"],
        "awayScore": match["score"]["fullTime"]["away"],
        "venue": match.get("venue", "情報なし") ,
        "competition": match["competition"]["name"],
        "matchday": match.get("matchday", ""),
        "homeTeamId": match["homeTeam"]["id"],
        "awayTeamId": match["awayTeam"]["id"],
        "matchId": match["id"]
    }