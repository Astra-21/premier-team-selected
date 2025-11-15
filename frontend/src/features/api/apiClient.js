import axios from 'axios';

const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials: true,
});


  
api.interceptors.response.use(
    response => response,
    error => {
        const status = error.response?.status;
        if (status === 401) {
            alert("認証エラー：再ログインしてください");
        } else if (status >= 500) {
            alert("サーバーエラーが発生しました。");
        }
        return Promise.reject(error);
    }
);
  
export default api;