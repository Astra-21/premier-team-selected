import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

from app import models
from app.database import engine
from app import auth, recommend, youtube



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



load_dotenv()

app = FastAPI()

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



app.include_router(recommend.router)
app.include_router(auth.router)
app.include_router(youtube.router)  



for model in genai.list_models():
    print(model.name)


#テーブル作成
models.Base.metadata.create_all(bind=engine)




