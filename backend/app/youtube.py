# app/youtube.py
from fastapi import APIRouter, HTTPException
import requests
import os

router = APIRouter()



TEAM_YOUTUBE_CHANNELS = {
    "Arsenal FC": "UCpryVRk_VDudG8SHXgWcG0w",
    "Aston Villa FC": "UCcUnrBEvRc4D3Zc_ArPQ1Wg",
    "Chelsea FC": "UCU2PacFf99vhb3hNiYDmxww",
    "Everton FC": "UCtK4QAczAN2mt2ow_jlGinQ",
    "Fulham FC": "UC2VLfz92cTT8jHIFOecC-LA",
    "Liverpool FC": "UC9LQwHZoucFT94I2h6JOcjw",
    "Manchester City FC": "UCkzCjdRMrW2vXLx8mvPVLdQ",
    "Manchester United FC": "UC6yW44UGJJBvYTlfC7CRg2Q",
    "Newcastle United FC": "UC4a2xdiT7xN0Yx3a9T5Dq1g",
    "Tottenham Hotspur FC": "UCEg25rdRZXg32iwai6N6l0w",
    "Wolverhampton Wanderers FC": "UCQ7Lqg5Czh5djGK6iOG53KQ",
    "Leicester City FC": "UCfYzv1N1eX6yHkK8rG4G1gQ",
    "Southampton FC": "UCxvXjfiIHQ2O6saVx_ZFqnw",
    "Ipswich Town FC": "UCjNwxJec96lMWgCXjEDhXgQ",
    "Nottingham Forest FC": "UCyAxjuAr8f_BFDGCO3Htbxw",
    "Crystal Palace FC": "UCs8xNLB7Eg-3t5nqGJ0sJ_w",
    "Brighton & Hove Albion FC": "UCf-cpC9WAdOsas19JHipukA",
    "Brentford FC": "UCi9x3MXxhh1K0UGDXc6K1mw",
    "West Ham United FC": "UC1I3G-Kb7l9RdpQKf_tI4-Q",
    "AFC Bournemouth": "UCrHgXvTqz3P-Mc7eUjW0ViA"
}


@router.get("/api/team/{team_name}/youtube")
def get_latest_video(team_name: str):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API key not set")

    channel_id = TEAM_YOUTUBE_CHANNELS.get(team_name)
    if not channel_id:
        raise HTTPException(status_code=404, detail="Unknown team")

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 1
    }
    
    r = requests.get(url, params=params)
    print("🌐 YouTube API URL:", r.url)
    print("📦 YouTube API Response:", r.text)

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="YouTube API error")

    data = r.json()
    items = data.get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="No videos found")

    video_id = items[0]["id"]["videoId"]
    return {"video_url": f"https://www.youtube.com/watch?v={video_id}"}




    


    