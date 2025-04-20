import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './loginPage';
import MyPage from './MyPage';
import SettingPage from './SettingPage';

const categories = {
  "サッカースタイル": ["ポゼッション", "カウンター", "バランス", "未記入"],
  "好きな色": ["赤", "青", "水", "白", "黒", "茶", "未記入"],
  "日本人選手": ["在籍している", "在籍していない", "未記入"],
  "昨季の順位": ["上位", "中位", "下位", "未記入"]
};

function DiagnosisPage() {
  const [selected, setSelected] = useState({
    "サッカースタイル": "未記入",
    "好きな色": "未記入",
    "日本人選手": "未記入",
    "昨季の順位": "未記入"
    
  });
  const [expanded, setExpanded] = useState(null);
  const [result, setResult] = useState(null);

  const handleSelect = (category, value) => {
    setSelected(prev => ({ ...prev, [category]: value }));
  };

  const handleSubmit = async () => {
    const res = await fetch(import.meta.env.VITE_API_ENDPOINT + '/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preferences: Object.values(selected) }) 
    });
    const data = await res.json();
    setResult(data);
    localStorage.setItem("recommendedTeam", data.team);  // ここで保存！
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-white p-6 flex items-center justify-center">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-2xl text-center">
        <h1 className="text-3xl font-bold mb-4">🏆 Premier League 診断</h1>
        <p className="text-gray-600 mb-8">4つの質問に答えて、あなたにぴったりのチームを診断しよう！</p>

        <div className="space-y-6">
          {Object.entries(categories).map(([cat, options]) => (
            <div key={cat}>
              <p className="font-semibold mb-2 text-left">{cat}</p>
              <div className="flex flex-wrap justify-center gap-2">
                {options.map(opt => (
                  <button
                    key={opt}
                    className={`px-4 py-2 rounded-full border ${
                      selected[cat] === opt
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 hover:bg-blue-100'
                    }`}
                    onClick={() => handleSelect(cat, opt)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-10">
          <button
            onClick={handleSubmit}
            className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-indigo-600 hover:to-blue-600 text-white py-3 px-6 rounded-full font-semibold shadow-md"
          >
            🚀 診断する
          </button>
        </div>

        {result && (
          <div className="mt-10 text-center">
            <h2 className="text-2xl font-bold">{result.team}</h2>
            <img src={result.logo} alt={result.team} className="mx-auto my-4 w-24 h-24" />
            <p className="text-gray-700">{result.info}</p>
            <div className="mt-4 space-x-4">
              <button onClick={() => window.location.href='/login'} className="px-4 py-2 bg-blue-400 text-white rounded">ログイン</button>
              <button onClick={() => window.location.href='/login'} className="px-4 py-2 bg-green-400 text-white rounded">新規登録</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
  
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DiagnosisPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/settings" element={<SettingPage />} />
      </Routes>
    </Router>
  );
}
