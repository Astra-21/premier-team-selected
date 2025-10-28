#apiから情報を取得するコード

import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Team, Player
from app.database import SessionLocal
from dotenv import load_dotenv
import os
from typing import List, Dict, Any

load_dotenv()  # .envを読み込む

API_URL = "https://api.football-data.org/v4/competitions/PL/teams"
API_TOKEN = os.getenv("YOUR_API_KEY")  # ← 自分のAPIキーに差し替えて

def fetch_teams_from_api():
    headers = {"X-Auth-Token": API_TOKEN}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    return response.json()["teams"]

def save_teams_to_db(db: Session, fetched_teams: List[Dict[str, Any]])->None:
    current_ids = {int(t["id"]) for t in fetched_teams}

    try:
        # 今年いない選手を先に削除（RESTRICTなので順序が先）
        if current_ids:
            db.query(Player).filter(~Player.team_id.in_(current_ids)).delete(synchronize_session=False)
        else:
            db.query(Player).delete(synchronize_session=False)
        

        # 今年いないチームを削除
        if current_ids:
            db.query(Team).filter(~Team.id.in_(current_ids)).delete(synchronize_session=False)
        else:
            db.query(Team).delete(synchronize_session=False)
        

        # 今年のチームを upsert（PK=外部IDを使う前提）
        for t in fetched_teams:
            db.merge(Team(id=int(t["id"]), name=t["name"], logo_url=t["crest"]))
        

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    




def main():
    db = SessionLocal()
    try:
        teams = fetch_teams_from_api()
        save_teams_to_db(db, teams)
        print("✅ チーム情報を保存しました。")
    finally:
        db.close()

if __name__ == "__main__":
    main()
