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
from . import models
from .database import get_db


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

#delete
@router.get("/protected")
async def protected_route(current_user: TokenData = Depends(get_current_user)):
    # ここでユーザー名とお気に入りチームのロゴをデータベースから取得する
    username = "サンプルユーザー"  # データベースから取得
    favorite_team_logo = "https://example.com/team_logo.png"  # データベースから取得
    return {"message": f"ログイン成功!Google ID: {current_user.google_id}", "username": username, "favoriteTeamLogo": favorite_team_logo}



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


class FavoriteUpdateRequest(BaseModel):
    favorite_team: str

user_data_store = {}
@router.post("/api/user/favorite")
async def set_favorite_team(
    request: FavoriteUpdateRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter_by(google_id=current_user.google_id).first()
    if not user:
        user = models.User(google_id=current_user.google_id, favorite_team=request.favorite_team)
        db.add(user)
    else:
        user.favorite_team = request.favorite_team
    db.commit()
    return {"status": "ok"}
   