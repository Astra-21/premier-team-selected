import { Routes, Route, BrowserRouter } from "react-router-dom";
import Diagnosis from "../pages/Diagnosis.jsx"
import Login from "../pages/Login.jsx";
import MyPage from "../pages/MyPage.jsx";
import Settings from "../pages/Settings.jsx";


const AppRoutes = () => (
    <BrowserRouter>
        <Routes>
            <Route path="/" element={<Diagnosis />} />
            <Route path="/login" element={<Login />} />
            <Route path="/mypage" element={<MyPage />} />
            <Route path="/settings" element={<Settings />} />
        </Routes>
    </BrowserRouter>
)
export default AppRoutes;