import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function MyPage() {
  const [username, setUsername] = useState("");
  const [favoriteTeam, setFavoriteTeam] = useState("");
  const [favoritePlayer, setFavoritePlayer] = useState("");
  const [logoUrl, setLogoUrl] = useState("");
  const [activeTab, setActiveTab] = useState("info");

  const navigate = useNavigate();

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
          <p className="text-gray-700">ユーザー名: <strong>{username}</strong></p>
          <p className="text-gray-700">推し選手: {favoritePlayer || "未設定"}</p>
        </div>
      )}

      {activeTab === "matches" && (
        <div className="space-y-3">
          <h3 className="text-xl font-semibold">直近の試合</h3>
          <p className="text-gray-600">ここに試合結果・スタッツなどが表示されます（API接続 or モック）</p>
        </div>
      )}
    </div>
  );
}

export default MyPage;

