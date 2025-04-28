import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Body
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models #これいる？
from app.database import get_db
from app.models import Team
from app.models import Player
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("YOUR_API_KEY")
HEADERS = {"X-Auth-Token": API_TOKEN}



SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    google_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        google_id: str = payload.get("sub")
        if google_id is None:
            raise credentials_exception
        token_data = TokenData(google_id=google_id)
    except JWTError:
        raise credentials_exception
    return token_data



class LoginRequest(BaseModel):
    google_id: str

@router.post("/login")
async def login(login_request: LoginRequest):
    id_token_str = login_request.google_id
    logging.debug(f"Received login request with google_id: {id_token_str}")
    try:
        idinfo = id_token.verify_token(
            id_token_str,
            grequests.Request(),
            "1080566879383-o9a4ft3uhqeuumpsl54ti7vt6r7c72t8.apps.googleusercontent.com"
        )

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


class FavoriteUpdateRequest(BaseModel):
    favorite_team: str
    favorite_player: str
    username: str  

class UpdateUsernameRequest(BaseModel):
    username: str



@router.get("/api/user/me")
async def get_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter_by(google_id=current_user.google_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    return {
        "username": user.username,
        "favorite_team": user.favorite_team,
        "favorite_player": user.favorite_player,
        "logo_url": user.logo_url
    }




user_data_store = {}
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