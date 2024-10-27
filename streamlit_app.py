import streamlit as st
import google.generativeai as genai
import os
import dotenv
from supabase import create_client, Client
from datetime import datetime

# 環境変数からAPIキーとSupabase接続情報を読み込み
dotenv.load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model_name = os.environ.get("GEMINI_MODEL_NAME", "gemini-1.5-pro")  # デフォルトモデル名を指定

supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

# 都道府県のリスト
prefectures = [
    "北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島",
    "茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川",
    "新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜",
    "静岡", "愛知", "三重", "滋賀", "京都", "大阪", "兵庫",
    "奈良", "和歌山", "鳥取", "島根", "岡山", "広島", "山口",
    "徳島", "香川", "愛媛", "高知", "福岡", "佐賀", "長崎",
    "熊本", "大分", "宮崎", "鹿児島", "沖縄"
]

# Streamlit UI
st.title("日本旅行モデルコース生成アプリ")
st.write(
    f"生成された旅行プランは生成AIで作成されており誤った情報が含まれている可能性があるため、"
    f"事実確認は自身で行うようにお願いします。AIモデル名: {model_name}"
)

# ユーザー入力
start = st.selectbox("出発する都道府県", prefectures, index=prefectures.index("東京"))
destination = st.selectbox("旅行先の都道府県", prefectures)
num_people = st.slider("人数", 1, 10, 1)
interests = st.multiselect(
    "興味の対象（複数選択可）", 
    ["温泉", "グルメ", "アクティビティ", "歴史", "博物館", "アニメ聖地巡礼", "自然", "アート", "Vtuber聖地巡礼"]
)
duration = st.slider("滞在日数", 1, 10, 1)
special_requests = st.selectbox(
    "特別リクエスト", 
    ["なし", "できるだけ多くまわりたい", "ゆっくりまわりたい", "値段を抑えて旅行したい", "Youtubeの動画ネタになるようきつい行程にしたい"]
)

# 入力検証
def validate_inputs(start, destination, num_people, interests, duration, special_requests):
    # 都道府県のチェック
    if start not in prefectures or destination not in prefectures:
        st.error("無効な都道府県が選択されました。")
        return False
    return True

# プロンプトを生成する関数
def create_travel_prompt(start, destination, num_people, interests, duration, special_requests):
    prompt = f"""
    日本旅行モデルコースを作成してください。
    - 出発する都道府県: {start}
    - 旅行先の都道府県: {destination}
    - 人数: {num_people}名
    - 興味の対象: {', '.join(interests)}
    - 滞在日数: {duration}日
    - 特別リクエスト: {special_requests}
    以上の条件に基づき、訪れるべき場所やアクティビティを含んだおすすめの旅行モデルコースと日ごとの予算と合計予算を提案してください。
    予算には交通費、宿泊費も含めてください。
    また情報元となるURL等も最後にできる限り記載してください。
    """
    return prompt

# 実行結果をSupabaseに保存する関数
def save_to_supabase(model_name, prompt, output_result, prompt_token_count, response_token_count, total_token_count):
    data = {
        "model_name": model_name,
        "prompt": prompt,
        "output_result": output_result,
        "prompt_token_count": prompt_token_count,
        "response_token_count": response_token_count,
        "total_token_count": total_token_count,
        "execution_time": datetime.now().isoformat()
    }
    response = supabase.from_("ai_execution_logs").insert(data).execute()
    if response.data:
        print("データが正常に保存されました")
    else:
        print("データ保存に失敗しました")

# Gemini AIへのリクエスト
if st.button("モデルコースを生成"):
    if interests and validate_inputs(start, destination, num_people, interests, duration, special_requests):
        travel_prompt = create_travel_prompt(start, destination, num_people, interests, duration, special_requests)
        model = genai.GenerativeModel(model_name)  # 環境変数から読み込んだモデル名を使用
        response = model.generate_content(
            travel_prompt,
            generation_config=genai.types.GenerationConfig(temperature=1.5),
        )
        st.write("生成されたモデルコース:")
        st.write(response.text)
        
        # コンソールに使用状況メタデータを正しく出力
        if response.usage_metadata:
            prompt_token_count = response.usage_metadata.prompt_token_count
            response_token_count = response.usage_metadata.candidates_token_count
            total_token_count = response.usage_metadata.total_token_count
            print(f"API使用状況メタデータ:")
            print(f"  プロンプトトークン数: {prompt_token_count}")
            print(f"  応答トークン数: {response_token_count}")
            print(f"  合計トークン数: {total_token_count}")

            # Supabaseに保存
            save_to_supabase(
                model_name, travel_prompt, response.text,
                prompt_token_count, response_token_count, total_token_count
            )
    else:
        st.warning("興味の対象を少なくとも1つ選択してください。")

# フッターの追加
st.markdown(
    """
    <hr style="border: none; border-top: 1px solid #ccc;"/>
    <div style="text-align: center;">
        <p>制作元: <a href="https://project-shangrila.github.io/" target="_blank">秋葉原IT戦略研究所</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
