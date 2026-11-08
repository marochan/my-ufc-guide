import os
import urllib.request
import json
import re
from google import genai
from google.genai import types

def fetch_espn_ufc_data():
    """ESPN公式APIから直近〜次回のUFC大会データ（カード・選手名・顔写真・オッズ）を取得"""
    url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return json.dumps(data, ensure_ascii=False)[:12000] # トークン上限内に収めて抽出
    except Exception as e:
        print(f"ESPN fetch warning: {e}")
        return "{}"

def generate():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)
    espn_raw = fetch_espn_ufc_data()

    system_instruction = """
あなたは総合格闘技（UFC）の専門リサーチャー兼スポーツアナリストです。
提供された最新の一次データ（ESPN API）を基盤に、スマートフォンで美しく読める観戦ガイド用のHTML（完全な単一ページ）を作成してください。

【時間・基準認識】
現在は「2026年11月」です。UFC Vegas 124（中村京一郎出場）は終了しました。過去大会を次回大会と誤認せず、次回開催の最新イベントを扱ってください。

【ノートブック確定執筆ルール】
1. 創作・脚色の完全禁止:
   架空の対戦カードや嘘の戦績は捏造しないこと。確認できないものは推測せず「確認できず」と明記すること。
2. 掲載順序の完全厳守（各試合内）:
   選手紹介・見どころのあとに続く予想およびスポンサー枠は、例外なく以下の相対順序を厳守すること:
   ① 有識者予想
   ② ほかの媒体の予想
   ③ 筆者予想
   ④ 予想の理由
   ⑤ スポンサー
3. 選手名と戦績表記:
   - 選手名はできる限りフルネーム（カタカナ）＋英字表記。
   - プロ戦績の直下にUFC戦績を配置。
   - フィニッシュ回数（KO/TKO、一本）をプロ・UFCそれぞれで明記すること。
4. 予想とオッズ:
   - 筆者予想は「勝者・決着方法（KO/一本/判定）・判定種別（全会一致/スプリット等）・ラウンド」まで詳細に記載。
   - 勝敗オッズは主要マネーラインのみ記載（個別のKO/一本オッズは記載しない）。
5. 視覚的・Web要素:
   - ESPNデータに含まれる選手ヘッドショット画像URL（png）を利用し、見出し直下に選手顔写真とESPNスタッツリンクを配置すること。
   - 「海外ファン・コミュニティの反応」枠を設け、現地ファンの主な論点を簡潔に記載すること。
"""

    prompt = f"""
以下はESPN公式データから取得した直近・次回のUFC大会データです:
{espn_raw}

このデータをベースに、次回UFC大会の観戦ガイドを完全な1枚のHTML（DOCTYPEから</html>まで）として出力してください。

【HTMLデザイン要件】
- スマホ閲覧に最適化されたモダンなダークモードデザイン（背景: #0f1115、カード背景: #181b22、文字: #e6edf3、アクセント: UFCレッド #d20a0a）
- CSSはすべて <style> タグ内に埋め込むこと
- 各試合カードは枠線で囲み、選手顔写真の横並び、テーブルによる基本データ比較、見出し付きの予想枠を整理して配置すること
"""

    # 429制限を回避するため、検索ツールなしの純粋な高速推論モデルを指定
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,
        ),
    )

    content = response.text

    # コードブロックタグの除去
    if content.startswith("```html"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # index.htmlに直接書き出し
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("Successfully generated index.html automatically!")

if __name__ == "__main__":
    generate()
