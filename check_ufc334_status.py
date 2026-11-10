import urllib.request
import json
import re
import sys
import os

print("=========================================================")
print("🔍 UFC 334 公式ステータス＆対戦カード自動差分チェッカー")
print("データソース: ESPN MMA Scoreboard API (一次情報)")
print("=========================================================\n")

# 1. サイト掲載のカード一覧
bouts_in_html = [
    ('Ciryl Gane', 'Josh Hokit'),
    ('Kayla Harrison', 'Amanda Nunes'),
    ('Caio Borralho', 'Yousri Belgaroui'),
    ('Uroš Medić', 'Kevin Holland'),
    ('Bilal Hasan', 'Luis Gurule'),
    ('Donte Johnson', 'Cesar Almeida'),
    ('Jim Miller', 'Terrance McKinney'),
    ('Drew Dober', 'Chris Duncan'),
    ('Stephen Thompson', 'Charles Radtke'),
    ('Evan Elder', 'Samuel Sanches'),
    ('Juan Diaz', 'Alatengheili / Adrian Yañez'),
    ('Macy Chiasson', 'Bia Mesquita'),
    ('Jared Gordon', 'Melquizael Costa')
]

url = 'https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

has_difference = False
summary_lines = []

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        events = data.get('events', [])
        if not events:
            print("❌ エラー: ESPN APIからイベントデータが取得できませんでした。")
            sys.exit(1)
        
        event = events[0]
        event_name = event.get('name', '')
        event_date = event.get('date', '')
        print(f"📡 取得イベント: {event_name} ({event_date})\n")
        
        competitions = event.get('competitions', [])
        print(f"📊 ESPN公式登録試合数: {len(competitions)} 試合")
        print(f"📄 本サイト掲載試合数: 13 試合\n")
        
        live_fighters = []
        live_pairings = []
        for comp in competitions:
            fighters = [c.get('athlete', {}).get('displayName', '') for c in comp.get('competitors', [])]
            status_type = comp.get('status', {}).get('type', {}).get('name', 'STATUS_SCHEDULED')
            live_pairings.append((fighters, status_type))
            live_fighters.extend(fighters)
        
        print("【全試合ステータス照合結果】")
        for i, (f1, f2) in enumerate(bouts_in_html, 1):
            matched = False
            f2_candidates = [x.strip() for x in f2.split('/')]
            for (lf, st) in live_pairings:
                has_f1 = any(f1.lower() in name.lower() or name.lower() in f1.lower() for name in lf)
                has_f2 = any(any(c.lower() in name.lower() or name.lower() in c.lower() for c in f2_candidates) for name in lf)
                if has_f1 and has_f2:
                    matched = True
                    tag = "正常一致"
                    if "Adrian Yañez" in " ".join(lf):
                        tag = "スクランブル代打参戦（公式反映待ち）"
                    line = f"✅ 第{i}戦: {f1} vs {f2_candidates[0]} -> [{tag} / {st}]"
                    print(f"  {line}")
                    summary_lines.append(f"- {line}")
                    break
                elif has_f1 or has_f2:
                    matched = True
                    has_difference = True
                    line = f"⚠️ 【カード変更検知】 第{i}戦: {f1} vs {f2} -> 最新: {' vs '.join(lf)} [{st}]"
                    print(f"  {line}")
                    summary_lines.append(f"- **{line}**")
                    break
            
            if not matched:
                has_difference = True
                line = f"❌ 【未検出/中止の可能性】 第{i}戦: {f1} vs {f2} がESPN公式で見つかりません"
                print(f"  {line}")
                summary_lines.append(f"- **{line}**")
        
        print("\n---------------------------------------------------------")
        if not has_difference and len(competitions) == 13:
            print("🎉 【公式確認完了】全13試合すべてESPN公式データと照合確認済みです。")
            print("   急な試合中止（Cancelled）は発生していません。")
            result_status = "SUCCESS"
        else:
            print("⚠️ 【要確認】ESPN公式データとの間に差分が検知されました。")
            print("   上記の差分詳細を確認し、index.htmlの更新を行ってください。")
            result_status = "WARNING"
        print("---------------------------------------------------------")

        # GitHub Actions Step Summary 出力
        step_summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
        if step_summary_file:
            with open(step_summary_file, 'a', encoding='utf-8') as f_sum:
                f_sum.write(f"## 🔍 UFC 334 公式ステータス自動照合レポート ({result_status})\n\n")
                f_sum.write(f"- **対象イベント**: {event_name} ({event_date})\n")
                f_sum.write(f"- **照合ステータス**: {'✅ 全試合一致・変更なし' if not has_difference else '⚠️ カード変更/要確認項目あり'}\n\n")
                f_sum.write("### 照合結果一覧\n")
                for s in summary_lines:
                    f_sum.write(s + "\n")

        # 差分検知時、GitHub Issue を自動起票してユーザーにプッシュ通知
        github_token = os.environ.get('GITHUB_TOKEN')
        github_repo = os.environ.get('GITHUB_REPOSITORY')
        if has_difference and github_token and github_repo:
            print("\n📢 差分検知に伴うGitHub Issue自動通知を処理中...")
            try:
                # 既存の未解決Issueを確認（重複通知防止）
                issues_url = f"https://api.github.com/repos/{github_repo}/issues?state=open"
                check_req = urllib.request.Request(issues_url, headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'UFC334-StatusChecker'
                })
                with urllib.request.urlopen(check_req, timeout=10) as resp_issue:
                    open_issues = json.loads(resp_issue.read().decode('utf-8'))
                    already_opened = any("UFC 334 カード変更検知" in iss.get('title', '') for iss in open_issues)
                
                if already_opened:
                    print("ℹ️ 既にオープン状態の通知Issueが存在するため、新規起票はスキップしました。")
                else:
                    issue_title = "🚨 【要確認】UFC 334 カード変更または試合中止を検知しました"
                    issue_body = (
                        "## 🚨 UFC 334 公式ステータス変更検知通知\n\n"
                        "ESPN MMA公式Scoreboard APIとの自動照合により、対戦カードの変更または試合中止の可能性が検知されました。\n\n"
                        "### 🔍 検知された照合結果\n"
                        + "\n".join(summary_lines) + "\n\n"
                        "### 🛠 推奨される対応手順\n"
                        "1. **帰宅後にPCで対応する場合（おすすめ）**:\n"
                        "   - Antigravityを開き、「カード変更があったのでindex.htmlに反映して」と一言指示してください。新選手の公式顔写真・戦績・年齢・直近3試合データが全自動で反映されます。\n"
                        "2. **外出先からスマホで即時対応する場合**:\n"
                        "   - リポジトリの `index.html` 最上部にある `🚨 【大会直前・公式LIVE速報】` バナーに1行メモを追記してコミットしてください。\n\n"
                        "> ※このIssueは GitHub Actions (check-status.yml) により自動起票されました。"
                    )
                    create_data = json.dumps({'title': issue_title, 'body': issue_body}).encode('utf-8')
                    post_req = urllib.request.Request(
                        f"https://api.github.com/repos/{github_repo}/issues",
                        data=create_data,
                        headers={
                            'Authorization': f'token {github_token}',
                            'Accept': 'application/vnd.github.v3+json',
                            'Content-Type': 'application/json',
                            'User-Agent': 'UFC334-StatusChecker'
                        }
                    )
                    with urllib.request.urlopen(post_req, timeout=10) as create_resp:
                        if create_resp.status in (200, 201):
                            print("✅ GitHub Issue を自動起票しました！スマホおよび登録メールへ通知が送信されます。")
            except Exception as ie:
                print(f"⚠️ Issue起票処理でエラーが発生しました (無視して続行): {ie}")

        # 差分検知時は exit code 0 で正常終了させつつ警告を出力
        sys.exit(0)

except Exception as e:
    print(f"❌ 通信エラー: {e}")
    sys.exit(1)
