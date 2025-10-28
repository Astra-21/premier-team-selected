# import_players.py
import os
import time
from typing import List, Dict, Any

import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Team, Player


# --- 設定 ---
API_TOKEN = os.getenv("YOUR_API_KEY")
API_BASE = "https://api.football-data.org/v4/teams/"
HEADERS = {"X-Auth-Token": API_TOKEN}
REQUEST_INTERVAL_SEC = 6  # 無料枠は 10 req/min 想定 → 6秒間隔


def fetch_players_from_team(team_id: int) -> List[Dict[str, Any]]:
    """
    football-data.org v4 の /teams/{id} から squad を取得して
    [{"id": 44, "name": "...", "position": "...", "team_id": 57}, ...] を返す
    """
    url = f"{API_BASE}{team_id}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    squad = data.get("squad", []) or []

    players: List[Dict[str, Any]] = []
    for p in squad:
        pid = p.get("id")
        name = p.get("name")
        # position が None のケースあり（GK/DF/MF/FW 以外など）
        position = p.get("position")

        if pid is None or name is None:
            # IDや名前が欠ける不完全データはスキップ
            continue

        players.append({
            "id": int(pid),
            "name": name,
            "position": position,
            "team_id": int(team_id),
        })
    return players


def refresh_all_players(db: Session) -> None:
    """
    現在の teams テーブルに存在する全チームを対象に、
    各チームの“名簿にいない選手”を削除 → 現在ロスターを upsert する。
    """
    # 今季のチーム一覧（import_teams 実行後を想定）
    team_ids = [tid for (tid,) in db.query(Team.id).all()]
    if not team_ids:
        print("⚠️ teams が空です。先に import_teams を実行してください。")
        return

    # --- ↓↓↓ ここから修正 ↓↓↓ ---

    # 1. まずAPIから全チームの全選手情報を取得し、一つのリストにまとめる
    all_roster_players = []
    for idx, tid in enumerate(team_ids):
        try:
            roster = fetch_players_from_team(tid)
            all_roster_players.extend(roster)
            print(f"✅ team_id={tid} の選手情報を取得しました。")
        except requests.HTTPError as e:
            print(f"❌ team_id={tid} の選手取得に失敗: {e}")
            continue
        except requests.RequestException as e:
            print(f"❌ team_id={tid} の通信エラー: {e}")
            continue
        
        # レート制限対策
        if idx < len(team_ids) - 1:
            time.sleep(REQUEST_INTERVAL_SEC)

    # 2. 今シーズン在籍する全選手のIDセットを作成
    current_player_ids = {int(p["id"]) for p in all_roster_players}

    # 3. DBにいるが、今季のロスターにいない選手を一括で削除
    if current_player_ids:
        db.query(Player).filter(
            ~Player.id.in_(current_player_ids)
        ).delete(synchronize_session=False)
    else:
        # 万が一、全選手情報が取得できなかった場合は全削除
        db.query(Player).delete(synchronize_session=False)

    # 4. 今季の全選手情報を一括でupsert
    for p in all_roster_players:
        db.merge(Player(
            id=int(p["id"]),
            name=p["name"],
            position=p.get("position"),
            team_id=int(p["team_id"]),
        ))


def main() -> None:
    if not API_TOKEN:
        print("❌ APIトークンが設定されていません。FOOTBALL_DATA_API_TOKEN または YOUR_API_KEY を環境変数に設定してください。")
        return

    with SessionLocal() as db:
        try:
            # ここでは “削除→upsert” を全チーム分まとめて 1 トランザクションで実行
            refresh_all_players(db)
            db.commit()
            print("✅ 全チームの選手情報を更新しました。")
        except SQLAlchemyError as e:
            db.rollback()
            print(f"❌ DBエラーによりロールバックしました: {e}")
            raise
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    main()
