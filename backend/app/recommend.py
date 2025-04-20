from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.recommend_logic import recommend_team  

router = APIRouter()

# リクエストBody定義
class UserInput(BaseModel):
    preferences: List[str]

@router.post("/recommend")
async def recommend_team_endpoint(user_input: UserInput):
    try:
        team_name = await recommend_team(user_input.preferences)
        return {"team": team_name}
    except Exception as e:
        return {"error": str(e)}
