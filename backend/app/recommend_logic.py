import google.generativeai as genai
import os

# .envからAPIキーを読み込む
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def recommend_team(user_inputs: list[str], team_list: list[str]) -> str:
    team_options = '\n'.join(team_list)

    prompt = f"""
    あなたはプレミアリーグの専門家です。
    次のユーザーの希望条件に最も合う、以下のチーム一覧の中から1チームだけ選び、チーム名だけを出力してください。

    【チーム一覧】
    {team_options}

    ※ユーザーの希望は順位順に重要度が高くなっています。

    1位：{user_inputs[0]}
    2位：{user_inputs[1]}
    3位：{user_inputs[2]}
    
    ユーザーの希望条件：
    {', '.join(user_inputs)}

    出力例: Manchester City FC
    ※チーム一覧にないチームは絶対に出力しないでください。
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
