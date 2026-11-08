import os
import datetime
from google import genai
from google.genai import types

def generate():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)

    # 執筆ルール・テンプレートをシステム指示として埋め込み
    system_instruction = """
あなたは総合格闘技（UFC）の専門リサーチャー兼ライターです。
以下のルールを例外なく厳格に守って記事を作成してください。

【最重要原則】
1. 創作・脚色の完全禁止:
   推測や架空の事実、存在しない発言は一切書いてはならない。
   選手エピソード、発言、戦績、スポンサー情報は必ず一次ソース（UFC公式、本人取材、Embedded、Countdown、メディア記事）に基づき、末尾に出典（[媒体名・記事名・日付](URL)）を明記すること。確認できないものは「確認できず」と書くこと。
2. 掲載順序の厳守（各試合内）:
   選手紹介・見どころのあとの予想・スポンサー部分は、必ず以下の相対順序を厳守すること:
   ① 有識者予想
   ② ほかの媒体の予想
   ③ 筆者予想
   ④ 予想の理由
   ⑤ スポンサー
3. 選手名と戦績表記:
   - 選手名はできる限りフルネーム（カタカナ）＋英字表記。
   - プロ戦績の直下にUFC戦績を配置。
   - フィニッシュ回数（KO/TKO、一本）をプロ・UFCそれぞれで明記すること。
4. 予想の粒度:
   - 有識者予想・筆者予想は「勝者・決着方法（KO/TKO/一本/判定）・判定種別（全会一致/スプリット等）・ラウンド」まで詳細に記載すること。
   - 勝敗オッズは主要マネーラインのみ記載（KO/一本/判定別の個別オッズは記載しない）。
5. 文体:
   客観的で落ち着いた常体（〜だ、〜である、〜と見る）。
"""

    prompt = """
次回開催の「UFC 334（マディソン・スクエア・ガーデン大会）」に向けた観戦ガイドを作成してください。

以下の情報をWeb検索・リサーチして最新の事実のみで構成してください:
- 最新の対戦カード一覧（直前のカード変更・欠場・代役参戦がないか確認）
- メインカードおよびプレリム主要カードの選手エピソード（公式Q&A、直近の取材、Embedded、Countdown、SNS、記者会見での本人の発言や生い立ち・競技背景）
- 各試合の戦術的な見どころ（試合で見たい攻防）
- 最新の勝敗オッズ（DraftKings等、取得元と確認日時を明記）
- 有識者予想、他メディア予想（CBS Sports、MMA Junkie等）、筆者としての戦術的予想と詳細な理由
- スポンサー情報（確認できるもののみ、不明な場合は未確認と明記）
- 基本データ、プロ・UFC戦績（フィニッシュ内訳含む）、直近の試合結果

出力は、そのままブラウザで美しく読めるHTML形式（UTF-8、レスポンシブデザイン対応、モダンで見やすいCSSスタイルを含む1枚の完全なHTML）で出力してください。
"""

    # Google Search Groundingを有効にして最新情報を収集
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[{"google_search": {}}],
            temperature=0.2, # 創作を防ぐため低めに設定
        ),
    )

    content = response.text

    # コードブロック（```html ... ```）が含まれる場合の除去
    if content.startswith("```html"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # index.htmlとして書き出し
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("Successfully generated index.html")

if __name__ == "__main__":
    generate()
