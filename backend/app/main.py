import logging
from fastapi import FastAPI, Request

logging.basicConfig(level=logging.DEBUG)
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.recommend import router
from app import auth      
from app.recommend_logic import recommend_team
from app import models
from app.database import engine
from app import auth, recommend, youtube  
from app import instagram  # ← 追加


load_dotenv()

app = FastAPI()
app.include_router(router)
app.include_router(auth.router)
app.include_router(youtube.router)  
app.include_router(instagram.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React側のURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 環境変数からAPIキーを取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini初期設定
genai.configure(api_key=GEMINI_API_KEY)

#テーブル作成
models.Base.metadata.create_all(bind=engine)




