import requests
from sqlalchemy.orm import Session
from app.models import Player, Team
from app.database import SessionLocal
from dotenv import load_dotenv
import os
import time

load_dotenv()
API_TOKEN = os.getenv("YOUR_API_KEY")
API_BASE = "https://api.football-data.org/v4/teams/"
HEADERS = {"X-Auth-Token": API_TOKEN}

def fetch_players_from_team(team_id):
    url = f"{API_BASE}{team_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("squad", [])

def save_players_to_db(team_id, players_data, db: Session):
    for p in players_data:
        player = Player(
            id=p["id"],
            name=p["name"],
            position=p.get("position", ""),
            team_id=team_id
        )
        db.merge(player)  # 既存なら更新、なければ追加
    db.commit()

def main():
    db = SessionLocal()
    try:
        teams = db.query(Team).all()
        print(f"💡 全 {len(teams)} チームの選手情報を取得中...")

        for team in teams:
            print(f"📥 {team.name} の選手を取得中...")

            try:
                players = fetch_players_from_team(team.id)
                save_players_to_db(team.id, players, db)
            except requests.exceptions.HTTPError as e:
                print(f"❌ {team.name} の選手取得に失敗: {e}")  # 🔧 追加・修正
                continue  # 🔧 追加・修正

            time.sleep(6)  # 🔧 レート制限対策（1分10回 = 6秒ごとに1回）

        print("✅ 全チームの選手情報を保存しました。")

    finally:
        db.close()

if __name__ == "__main__":
    main()

