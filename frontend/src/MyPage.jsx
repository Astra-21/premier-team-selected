import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function MyPage() {
  const [username, setUsername] = useState("");
  const [favoriteTeam, setFavoriteTeam] = useState("");
  const [favoritePlayer, setFavoritePlayer] = useState("");
  const [logoUrl, setLogoUrl] = useState("");
  const [activeTab, setActiveTab] = useState("info");
  const [matchData, setMatchData] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState(null);
  const [instagramUrl, setInstagramUrl] = useState(null);



  const navigate = useNavigate();

  const fetchTeamIdByName = async (teamName) => {
    try {
      const res = await axios.get("http://localhost:8000/api/teams");
      
      const normalize = str => str.toLowerCase().replace(" fc", "").trim();//より柔軟に
      const team = res.data.find(t => normalize(t.name) === normalize(teamName));

      return team ? team.id : null;
    } catch (err) {
      console.error("チーム一覧の取得に失敗", err);
      return null;
    }
  };
  

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("accessToken");

      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const response = await axios.get("http://localhost:8000/api/user/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = response.data;
        setUsername(data.username);
        setFavoriteTeam(data.favorite_team);
        setFavoritePlayer(data.favorite_player);
        setLogoUrl(data.logo_url);
      } catch (err) {
        console.error(err);
        navigate("/login");
      }
    };

    fetchUserInfo();
  }, [navigate]);

  useEffect(() => {
    const fetchMatch = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token || !favoriteTeam) return;
  
      const teamId = await fetchTeamIdByName(favoriteTeam);
      if (!teamId) {
        console.warn("チームIDが見つかりませんでした");
        return;
      }
  
      try {
        const res = await axios.get(`http://localhost:8000/api/team/${teamId}/latest-match`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setMatchData(res.data);
      } catch (err) {
        console.error("試合データ取得失敗", err);
      }
    };
  
    if (activeTab === "matches") {
      fetchMatch();
    }
  }, [activeTab, favoriteTeam]); // ← favoriteTeam を依存に追加

  useEffect(() => {
    const fetchYouTube = async () => { //activeTab === "info" のとき
      const token = localStorage.getItem("accessToken");
      if (!token || !favoriteTeam || activeTab !== "info") return;
  
      try {
        const res = await axios.get(`http://localhost:8000/api/team/${favoriteTeam}/youtube`);
        setYoutubeUrl(res.data.video_url);
      } catch (err) {
        console.error("YouTube動画取得失敗", err);
      }
    };
  
    fetchYouTube();
  }, [activeTab, favoriteTeam]);

  useEffect(() => {
    const fetchInstagram = async () => {
      if (!favoriteTeam || activeTab !== "info") return;
  
      try {
        const res = await axios.get(`http://localhost:8000/api/team/${favoriteTeam}/instagram`);
        setInstagramUrl(res.data);
      } catch (err) {
        console.error("Instagram取得失敗", err);
      }
    };
  
    fetchInstagram();
  }, [activeTab, favoriteTeam]);
  
  

  
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center border-b pb-4 mb-4">
        <div className="flex items-center">
          {logoUrl && <img src={logoUrl} alt="チームロゴ" className="h-10 w-10 mr-3" />}
          <h2 className="text-2xl font-bold">{favoriteTeam}</h2>
        </div>
        <button
          onClick={() => navigate("/settings")}
          className="text-2xl hover:rotate-45 transition-transform"
        >
          ⚙
        </button>
      </div>

      {/* タブボタン */}
      <div className="flex space-x-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab("info")}
          className={`py-2 px-4 border-b-2 ${activeTab === "info" ? "border-blue-500 text-blue-600 font-semibold" : "border-transparent text-gray-500"}`}
        >
          チーム情報
        </button>
        <button
          onClick={() => setActiveTab("matches")}
          className={`py-2 px-4 border-b-2 ${activeTab === "matches" ? "border-blue-500 text-blue-600 font-semibold" : "border-transparent text-gray-500"}`}
        >
          試合データ
        </button>
      </div>

      {/* タブコンテンツ */}
{activeTab === "info" && (
  <div className="space-y-3">
    <h3 className="text-xl font-semibold">{favoriteTeam} 情報</h3>
    <p className="text-gray-700">ユーザー名: <strong>{username || "未設定 設定から変更できます"}</strong></p>
    <p className="text-gray-700">推し選手: {favoritePlayer || "未設定 設定から変更できます"}</p>

    {youtubeUrl && (
      <div className="mt-4 space-y-1">
        <h4 className="text-md font-semibold">YouTube 最新動画</h4>
        <div className="w-full max-w-2xl mx-auto aspect-video">
        <iframe
          className="w-full h-full"
          src={youtubeUrl.replace("watch?v=", "embed/")}
          title="YouTube video player"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
        </div>
        <a href={youtubeUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
          YouTube で開く
        </a>
      </div>
    )}

{instagramUrl && (
  <div className="mt-4 space-y-1">
    <h4 className="text-md font-semibold">Instagram 最新画像</h4>
    <img
      src={instagramUrl}
      alt="Instagram profile"
      className="w-32 h-32 rounded-full mx-auto"
    />
    <a
      href={`https://www.instagram.com/${TEAM_INSTAGRAM_HANDLES[favoriteTeam] || favoriteTeam.replace(" FC", "").replace(/\s+/g, "").toLowerCase()}`}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 underline block mt-2"
    >
      Instagram公式ページを見る
    </a>
  </div>
)}



  </div>
)}


      {activeTab === "matches" && (
        <div className="space-y-3">
          <h3 className="text-xl font-semibold">直近の試合</h3>
          {matchData ? (
            <div className="bg-white shadow-md rounded-lg p-4 space-y-3">
              <div className="text-gray-500 text-sm">
                {matchData.utcDate?.slice(0, 10) || "日付不明"} | {matchData.competition || "大会不明"} 第{matchData.matchday || "?"}節
              </div>
              <div className="flex justify-between items-center text-2xl font-bold">
                <span>{matchData.homeTeam || "不明"}</span>
                <span>
                  {(matchData?.homeScore ?? "-")} - {(matchData?.awayScore ?? "-")}
                </span>
                <span>{matchData.awayTeam || "不明"}</span>
              </div>
              <div className="text-gray-500 text-sm">
                開催地: {matchData.venue || "情報なし"}
              </div>
            </div>
          ) : (
            <p>読み込み中...</p>
          )}

        </div>
      )}

    </div>
  );
}

export default MyPage;

