// SettingPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function SettingPage() {
  const [favoritePlayer, setFavoritePlayer] = useState("");
  const [favoriteTeam, setFavoriteTeam] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("accessToken");

    try {
      await axios.post(
        "http://localhost:8000/api/user/favorite",
        {
          favorite_team: favoriteTeam,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // 成功したらマイページに戻る
      navigate("/mypage");
    } catch (err) {
      console.error("保存に失敗しました", err);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">設定ページ</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 font-semibold">推し選手（ダミー）</label>
          <input
            type="text"
            value={favoritePlayer}
            onChange={(e) => setFavoritePlayer(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="例：三笘薫"
          />
        </div>
        <div>
          <label className="block mb-1 font-semibold">お気に入りチーム</label>
          <input
            type="text"
            value={favoriteTeam}
            onChange={(e) => setFavoriteTeam(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="例：Arsenal"
            required
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
        >
          変更を保存
        </button>
      </form>
    </div>
  );
}

export default SettingPage;