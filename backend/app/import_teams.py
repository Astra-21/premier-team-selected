#apiから情報を取得するコード

import requests
from sqlalchemy.orm import Session
from app.models import Team
from app.database import SessionLocal
from dotenv import load_dotenv
import os

load_dotenv()  # .envを読み込む

API_URL = "https://api.football-data.org/v4/competitions/PL/teams"
API_TOKEN = os.getenv("YOUR_API_KEY")  # ← 自分のAPIキーに差し替えて

def fetch_teams_from_api():
    headers = {"X-Auth-Token": API_TOKEN}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    return response.json()["teams"]

def save_teams_to_db(teams_data, db: Session):
    for team in teams_data:
        db_team = Team(
            id=team["id"],
            name=team["name"],
            logo_url=team["crest"]
        )
        db.merge(db_team)  # 既にあれば更新・なければ追加
    db.commit()

def main():
    db = SessionLocal()
    try:
        teams = fetch_teams_from_api()
        save_teams_to_db(teams, db)
        print("✅ チーム情報を保存しました。")
    finally:
        db.close()

if __name__ == "__main__":
    main()
