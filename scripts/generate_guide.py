import os
import urllib.request
import urllib.parse
import json
import re
from google import genai
from google.genai import types

def search_web(query, max_results=3):
    """DuckDuckGoの軽量APIを使って最新Web情報を検索・取得（完全無料・APIキー不要）"""
    encoded = urllib.parse.quote(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = []
            if data.get("AbstractText"):
                results.append(data["AbstractText"])
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(topic["Text"])
            return "\n".join(results)
    except Exception as e:
        print(f"Search warning for '{query}': {e}")
        return ""

def generate():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)

    # 次回開催のUFC大会や最新カード情報を検索してコンテキスト化
    print("Searching for upcoming UFC event information...")
    search_context_1 = search_web("next UFC fight event card date odds")
    search_context_2 = search_web("UFC upcoming events official schedule")
    search_context_3 = search_web("UFC latest news embedded countdown")

    combined_context = f"""
【最新のWeb検索リサーチ結果】
{search_context_1}
{search_context_2}
{search_context_3}
"""

    system_instruction = """
あなたは総合格闘技（UFC）の専門リサーチャー兼ライターです。
以下のルールを例外なく厳格に守って記事を作成してください。

【最重要執筆ルール】
1. 現在の日時基準:
   現在は2026年11月です。「2025年現在」といった過去の基準で書かないこと。
2. 創作・脚色の完全禁止:
   推測や架空の事実、存在しない発言は一切書いてはならない。
   事実に基づき、末尾に出典（[媒体名・記事名・日付](URL)）を明記すること。確認できないものは「確認できず」と書くこと。
3. 掲載順序の厳守（各試合内）:
   選手紹介・見どころのあとの予想・スポンサー部分は、必ず以下の相対順序を厳守すること:
   ① 有識者予想
   ② ほかの媒体の予想
   ③ 筆者予想
   ④ 予想の理由
   ⑤ スポンサー
4. 選手名と戦績表記:
   - 選手名はできる限りフルネーム（カタカナ）＋英字表記。
   - プロ戦績の直下にUFC戦績を配置。
   - フィニッシュ回数（KO/TKO、一本）をプロ・UFCそれぞれで明記すること。
5. 予想の粒度:
   - 有識者予想・筆者予想は「勝者・決着方法（KO/TKO/一本/判定）・判定種別（全会一致/スプリット等）・ラウンド」まで詳細に記載すること。
   - 勝敗オッズは主要マネーラインのみ記載（KO/一本/判定別の個別オッズは記載しない）。
6. 文体:
   客観的で落ち着いた常体（〜だ、〜である、〜と見る）。
"""

    prompt = f"""
以下は直近のWeb検索情報です:
{combined_context}

現在（2026年11月）から見て、直近で開催される次回UFC大会の観戦ガイドを作成してください。

【必須構成】
- 大会概要（次回大会名、開催地、開催日時・日本時間視聴案内）
- 対戦カード紹介（メイン、主要カード）
- 各選手のバックボーン・生い立ち・競技の動機（事実のみ、出典明記）
- 試合で見たい攻防（筆者の見立て）
- 確定順序の厳守: 有識者予想 → ほかの媒体の予想 → 筆者予想 → 予想の理由 → スポンサー
- 基本データ・プロ戦績・UFC戦績（フィニッシュ内訳）

スマートフォンからそのまま美しく読めるモダンな1枚のHTML（レスポンシブデザイン、ダークモード基調、読みやすいCSSカードスタイル組み込み）として出力してください。
"""

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        ),
    )

    content = response.text

    if content.startswith("```html"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("Successfully generated up-to-date index.html!")

if __name__ == "__main__":
    generate()
