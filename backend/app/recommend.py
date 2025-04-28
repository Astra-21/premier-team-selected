# recommend.py
from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.recommend_logic import recommend_team  
from app.database import get_db
from app.models import Team

router = APIRouter()

class UserInput(BaseModel):
    preferences: List[str]

@router.post("/recommend")
async def recommend_team_endpoint(user_input: UserInput, db: Session = Depends(get_db)):
    try:
        # ここでDBからチーム一覧を取る
        teams = db.query(Team).all()
        team_list = [team.name for team in teams]

        # recommend_teamにチームリストも渡す！
        team_name = await recommend_team(user_input.preferences, team_list)
        return {"team": team_name}
    except Exception as e:
        return {"error": str(e)}
