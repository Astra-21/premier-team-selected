# app/instagram.py
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()

TEAM_INSTAGRAM_HANDLES = {
    "Arsenal FC": "arsenal",
    "Chelsea FC": "chelseafc",
    "Liverpool FC": "liverpoolfc",
    "Manchester City FC": "mancity",
    "Manchester United FC": "manchesterunited",
    "Tottenham Hotspur FC": "spursofficial",
    "Brighton & Hove Albion FC": "officialbhafc",
    "West Ham United FC": "westham",
    "Aston Villa FC": "avfcofficial",
    "Crystal Palace FC": "cpfc",
    "Newcastle United FC": "nufc",
    "Fulham FC": "fulhamfc",
    "Brentford FC": "brentfordfc",
    "Wolverhampton Wanderers FC": "wolves",
    "Everton FC": "everton",
    "Leicester City FC": "lcfc",
    "Southampton FC": "southamptonfc",
    "Nottingham Forest FC": "officialnffc",
    "AFC Bournemouth": "afcb",
    "Ipswich Town FC": "ipswichtown"
}

@router.get("/api/team/{team_name}/instagram")
def get_latest_instagram_post(team_name: str):
    handle = TEAM_INSTAGRAM_HANDLES.get(team_name)
    if not handle:
        raise HTTPException(status_code=404, detail="Instagram handle not found")

    url = f"https://www.instagram.com/{handle}/?__a=1&__d=dis"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()

        # 最新投稿情報を取得
        edges = data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
        if not edges:
            raise Exception("No posts found")

        latest_post = edges[0]["node"]
        shortcode = latest_post["shortcode"]
        thumbnail_url = latest_post["thumbnail_src"]

        return {
            "post_url": f"https://www.instagram.com/p/{shortcode}/",
            "thumbnail_url": thumbnail_url
        }

    except Exception as e:
        print("Instagram scrape error:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch Instagram post")
