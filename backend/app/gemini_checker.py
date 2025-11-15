import google.generativeai as genai
import os

# .envからAPIキーを読み込む
# ↓↓↓↓↓↓ この2行を追加 ↓↓↓↓↓↓
from dotenv import load_dotenv
load_dotenv()
# ↑↑↑↑↑↑ ここまで追加 ↑↑↑↑↑↑

# APIキーをハードコードせず、環境変数から取得する
# ↓↓↓↓↓↓ この行を修正 ↓↓↓↓↓↓
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("エラー: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    exit()

genai.configure(api_key=api_key) 
# ↑↑↑↑↑↑ ここまで修正 ↑↑↑↑↑↑

print("Available models:")
for model in genai.list_models():
  # generateContent がサポートされているモデルのみ表示（推奨）
  if 'generateContent' in model.supported_generation_methods:
    print(model.name)