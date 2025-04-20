import google.generativeai as genai
import os

# .envからAPIキーを読み込む
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def recommend_team(user_inputs: list[str]) -> str:
    prompt = f"""
    あなたはプレミアリーグの専門家です。
    次のユーザーの希望条件に最も合う1チームだけ選び、チーム名だけを出力してください。

    ユーザーの希望条件：
    {', '.join(user_inputs)}

    出力例: Arsenal
    ※チーム名だけ返してください。
    """

    model = genai.GenerativeModel('models/gemini-1.5-pro')  

    response = await model.generate_content_async(
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        generation_config={
            "temperature": 0.5,
            "max_output_tokens": 20,
        }
    )

    # レスポンスの取得方法もv1対応
    candidate = response.candidates[0]
    team_name = candidate.content.parts[0].text.strip()

    return team_name
