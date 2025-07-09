import React, { useState } from 'react';
import api from '../features/api/apiClient';
import { useNavigate } from 'react-router-dom';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';


const clientId = "660638373406-9h904j2eq11m12edst37q185lm0j7it2.apps.googleusercontent.com"; 

function LoginPage() {
    const [error, setError] = useState('');
    const navigate = useNavigate();

    //asyncでawaitが使えるように,credentialResponseを引数で受け取る。
    const onSuccess = async (credentialResponse) => {

        console.log("Redirect URI:", "http://localhost:5173/mypage");

        try {

            //右辺がGoogleが発行する id_token(JWT形式）, サーバー側で検証できるようになっているのが強み。
            //これは「このユーザーは Google によって正当に認証されましたよ」という証拠。
            //JWT形式のトークンで、ユーザーの身元情報（emailやsubなど）がエンコード済み
            //Google のライブラリが自動で返してくる構造
            
            const id_token = credentialResponse.credential;

            //Googleから取得したID Tokenをサーバーに渡して、JWTを受け取る非同期通信を可能に
            //サーバーからのレスポンスを待ち、その中身を使って localStorage に保存するのが「順番どおりに」できてる

            const response = await api.post("/login", {
              google_id: id_token,
            });

            const accessToken = response.data.access_token;
            localStorage.setItem("accessToken", accessToken);

            // 推薦されたチームがあれば保存
            const team = localStorage.getItem("recommendedTeam");
            
            if (team) {
                await api.post("/api/user/favorite", {
                    favorite_team: team,
                    favorite_player: "未選択",
                    username: "未選択"   
                });

                localStorage.removeItem("recommendedTeam");
            }
            
            navigate("/mypage");

        } catch (err) {
          const status = err.response?.status;

          if (status === 400) {
            setError("トークンが不正です。");
          } else if (status === 422) {
            setError("送信データの形式が正しくありません。");
          } else if (!err.response) {
            setError("ネットワークエラー：接続できませんでした。");
          } else {
            setError(`不明なエラー（コード: ${status}）`);
          }
        
          console.error("詳細エラー:", err);
        }
    };

    const onFailure = () => {
        setError("Googleログインに失敗しました。");
    };



    //@react-oauth/googleライブラリを使う、<GoogleOAuthProvider> :React上で動くための土台 を提供するコンポーネント
    //cosole で作ったclientId  アプリID でGoogleがこのリクエストは正規のアプリから来たものだと認識させる（必須）

    //<GoogleLogin>:Googleのログインボタンを表示し、ログイン処理をトリガーするUIコンポーネント
    //ユーザーがボタンを押し、Googleアカウントで認証(メアドとパス)されると、Googleがトークンを発行して、
    // credentialResponseが渡されonSuccess関数が発火

    return (
        <div>
            <h1>ログインページ</h1>
            <GoogleOAuthProvider clientId={clientId}>
            <GoogleLogin
                onSuccess={onSuccess}
                onError={onFailure}
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
