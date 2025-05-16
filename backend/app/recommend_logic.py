import re
import google.generativeai as genai
import os
import json

# .envからAPIキーを読み込む
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("[DEBUG] GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))

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

        【出力ルール】
        - JSON形式で返してください（他の文章や解説は一切含めないでください）,コードブロック記法も禁止
        - 以下の形式に厳密に従ってください：

        {{ "team": "Manchester City FC" }}

        ※チーム一覧にないチームは絶対に出力しないでください。
        ※JSONの形式は絶対に守ってください。
    """


    
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')


    response = await model.generate_content_async(
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        generation_config={"temperature": 0.5, "max_output_tokens": 50}
    )

    try:
        text = response.candidates[0].content.parts[0].text.strip()
        # デバッグ出力
        print("Gemini応答:", repr(text))  # reprで改行や空白も見えるようにする

        # 空チェック
        if not text:
            raise ValueError("Geminiの応答が空です")

        # コードブロック（```json）を除去
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)  # 最初の ```json\n を除去
            text = text.rstrip("```").strip()            # 最後の ``` を除去

        #print("整形後のJSON:", text)

        parsed = json.loads(text)

        print("パース後:",parsed)

        return parsed.get("team", "該当チームなし")
    
    except Exception as e:
        print("JSON形式で返ってこなかったエラー:", e)
        return "該当チームなし"
