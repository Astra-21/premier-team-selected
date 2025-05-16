import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function SettingPage() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [username, setUsername] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("accessToken");
      try {
        const res = await axios.get("http://localhost:8000/api/user/me", {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = res.data;
        setUsername(data.username);  // ← ここでDBから取得して初期化
      } catch (err) {
        console.error("ユーザー情報取得エラー:", err);
      }
    };
  
    fetchUserInfo();
  }, []);
  

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/teams");
        setTeams(response.data);
      } catch (error) {
        console.error("チーム取得エラー:", error);
      }
    };
    fetchTeams();
  }, []);

  // チームを選択したら選手も取得
  useEffect(() => {
    const fetchPlayers = async () => {
      if (!selectedTeam) return;
      try {
        const res = await axios.get(`http://localhost:8000/api/teams/${selectedTeam.id}/players`);
        setPlayers(res.data);
      } catch (err) {
        console.error("選手取得エラー:", err);
      }
    };
    fetchPlayers();
  }, [selectedTeam]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("accessToken");
    try {
      await axios.post("http://localhost:8000/api/user/favorite", {
        favorite_team: selectedTeam.name,
        favorite_player: selectedPlayer.name,
        username: username
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      navigate("/mypage");
    } catch (err) {
      console.error("保存エラー:", err);
    }
  };

  const handleUsernameUpdate = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("accessToken");
    try {
      await axios.post("http://localhost:8000/api/user/username", {
        username: username
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("ユーザー名を更新しました");
      navigate("/mypage"); 
    } catch (err) {
      console.error("ユーザー名更新エラー:", err);
    }
  };
  

  return (
    <div className="p-6 max-w-3xl mx-auto">

      <h1 className="text-2xl font-bold mb-4">ユーザ－名を選択</h1>
      <form onSubmit={handleUsernameUpdate}>
        <label className="block font-semibold mb-2">ユーザー名</label>
        <input
          type="text"
          className="w-full border px-3 py-2 rounded mb-2"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="表示するユーザー名を入力"
          required
        />
        <button
          type="submit"
          className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded"
        >
          ユーザー名を更新
        </button>
      </form>

      <h1 className="text-2xl font-bold mb-4">お気に入りチーム & 推し選手を選択</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* チーム選択 */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {teams.map(team => (
            <div
              key={team.id}
              onClick={() => {
                setSelectedTeam(team);
                setSelectedPlayer(null);  // 前回選択をリセット
              }}
              className={`cursor-pointer p-4 border rounded-xl text-center transition ${
                selectedTeam?.id === team.id
                  ? "border-blue-500 bg-blue-50"
                  : "hover:bg-gray-100"
              }`}
            >
              <img src={team.logo_url} alt={team.name} className="h-12 mx-auto mb-2" />
              <p className="text-sm">{team.name}</p>
            </div>
          ))}
        </div>

        {/* 選手選択 */}
        {players.length > 0 && (
          <div>
            <label className="block font-semibold mb-2">推し選手を選んでください</label>
            <select
              className="w-full border px-3 py-2 rounded"
              value={selectedPlayer?.id || ""}
              onChange={(e) => {
                const player = players.find(p => p.id === parseInt(e.target.value));
                setSelectedPlayer(player);
              }}
              required
            >
              <option value="" disabled>選手を選択</option>
              {players.map(p => (
                <option key={p.id} value={p.id}>{p.name}（{p.position}）</option>
              ))}
            </select>
          </div>
        )}

        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded disabled:opacity-50"
          disabled={!selectedTeam || !selectedPlayer}
        >
          変更を保存
        </button>
      </form>
    </div>
  );
}

export default SettingPage;

