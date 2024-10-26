import google.generativeai as genai
import os
import dotenv

# 環境変数からAPIキーを読み込み
dotenv.load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def create_travel_prompt(start, destination, num_people, interests, duration, special_requests):
    # Gemini AIに送信するプロンプトのテンプレートを生成
    prompt = f"""
    日本旅行モデルコースを作成してください。
    - 出発する都道府県: {start},
    - 旅行先の都道府県: {destination}
    - 人数: {num_people}
    - 興味の対象: {interests}
    - 滞在日数: {duration}
    - 特別リクエスト: {special_requests}
    以上の条件に基づき、訪れるべき場所やアクティビティを含んだおすすめの旅行モデルコースと日ごとの予算と合計予算を提案してください。
    予算には交通費、宿泊費も含めてください。
    """

    return prompt

# 入力情報（例）
start = "東京"
destination = "熊本"
num_people = "1人"
interests = "歴史、食、博物館、アニメ"
duration = "3日"
special_requests = "ゆっくり観光したい" #なし、できるだけ多くまわりたい

# プロンプトを生成
travel_prompt = create_travel_prompt(start, destination, num_people, interests, duration, special_requests)

# Gemini AIを使用してモデルコースを生成
# gemini-1.5-pro-latest
model = genai.GenerativeModel("gemini-1.5-pro")

print("total_tokens: ", model.count_tokens(travel_prompt))

response = model.generate_content(
    travel_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=1.0,
    ),
    )
print(response.text)

print(response.usage_metadata)