import os
import urllib.request
import re
from google import genai
from google.genai import types

def fetch_ufc_text():
    """UFC公式大会ページ等のテキスト情報を簡易取得（クォータ節約用）"""
    url = "https://www.ufc.com/events"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # HTMLタグを簡易除去してテキストを抽出
            text = re.sub(r'<[^>]+>', ' ', html)
            text = ' '.join(text.split())
            return text[:4000] # トークン節約のため冒頭4000文字
    except Exception as e:
        print(f"Fetch warning: {e}")
        return "UFC Event Information"

def generate():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)
    scraped_context = fetch_ufc_text()

    # note確定テンプレートと執筆ルール
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

    prompt = f"""
以下は直近のUFC公開情報の一部です:
{scraped_context}

次回開催の「UFC 334（マディソン・スクエア・ガーデン大会）」に向けた観戦ガイドを作成してください。

【必須構成】
- 大会概要（開催日・MSG・日本時間視聴案内）
- 対戦カード紹介（シリル・ガヌ vs ジョシュ・ホキット、ケイラ・ハリソン vs アマンダ・ヌネス、カイオ・ボハーリョ vs ユズリ・ベルガウイ、ケヴィン・ホランド、スティーブン・トンプソン、ジム・ミラー等）
- 選手ごとの生い立ち、格闘技のきっかけ、家族や競技への思い（事実のみ、出典明記）
- 試合で見たい攻防（筆者の見立て）
- 確定順序の厳守: 有識者予想 → ほかの媒体の予想 → 筆者予想 → 予想の理由 → スポンサー
- 基本データ・プロ戦績・UFC戦績（フィニッシュ内訳）

スマートフォンからそのまま美しく読めるモダンな1枚のHTML（レスポンシブデザイン、ダークモード基調、見やすいカード形式CSS組み込み）として出力してください。
"""

    # 外部Web検索ツールを外し、純粋なプロンプト処理にすることで429クォータ超過を回避
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
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

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("Successfully generated index.html without quota overflow!")

if __name__ == "__main__":
    generate()
