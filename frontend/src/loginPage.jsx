import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const clientId = "1080566879383-o9a4ft3uhqeuumpsl54ti7vt6r7c72t8.apps.googleusercontent.com"; 

function LoginPage() {
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const onSuccess = async (credentialResponse) => {
        console.log("Redirect URI:", "http://localhost:5173/mypage");
        try {
            const id_token = credentialResponse.credential;
            const response = await axios.post(
                "http://localhost:8000/login",
                {
                    google_id: id_token,
                },
                {
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            const accessToken = response.data.access_token;
            localStorage.setItem("accessToken", accessToken);

            // 推薦されたチームがあれば保存
            const team = localStorage.getItem("recommendedTeam");
            if (team) {
                await axios.post("http://localhost:8000/api/user/favorite", {
                    favorite_team: team
                }, {
                    headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": "application/json"
                    }
                });
                localStorage.removeItem("recommendedTeam"); // 保存後は消す
            }
            
            navigate("/mypage");
        } catch (err) {
            console.error("Login error:", err);
            setError("ログインに失敗しました。" + err.message);
        }
    };

    const onFailure = () => {
        setError("Googleログインに失敗しました。");
    };

    return (
        <div>
            <h1>ログインページ</h1>
            <GoogleOAuthProvider clientId={clientId}>
            <GoogleLogin
                onSuccess={onSuccess}
                onError={onFailure}
                useOneTap
                ux_mode="popup"
                redirectUri="http://localhost:5173/login"
                text="Googleでログイン"
                scope="openid profile email"
            />
            </GoogleOAuthProvider>
            {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
    );
}

export default LoginPage;
