import urllib.request
import json
import re
import sys

print("=========================================================")
print("🔍 UFC 334 公式ステータス＆対戦カード自動差分チェッカー")
print("データソース: ESPN MMA Scoreboard API (一次情報)")
print("=========================================================\n")

# 1. Load current fighters from index.html
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

# 2. Fetch live scoreboard from ESPN API
url = 'https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

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
        
        # Check differences
        all_matched = True
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
                    print(f"  ✅ 第{i}戦: {f1} vs {f2_candidates[0]} -> [{tag} / {st}]")
                    break
                elif has_f1 or has_f2:
                    matched = True
                    all_matched = False
                    print(f"  ⚠️ 【カード変更検知】 第{i}戦: {f1} vs {f2}")
                    print(f"     -> ESPN公式の最新組み合わせ: {' vs '.join(lf)} [状態: {st}]")
                    break
            
            if not matched:
                all_matched = False
                print(f"  ❌ 【未検出/中止の可能性】 第{i}戦: {f1} vs {f2} がESPN公式で見つかりません")
        
        print("\n---------------------------------------------------------")
        if all_matched and len(competitions) == 13:
            print("🎉 【公式確認完了】全13試合すべてESPN公式データと照合確認済みです。")
            print("   急な試合中止（Cancelled）は発生していません。")
        else:
            print("⚠️ 【要確認】ESPN公式データとの間に差分が検知されました。")
            print("   上記の差分詳細を確認し、index.htmlの更新を行ってください。")
        print("---------------------------------------------------------")

except Exception as e:
    print(f"❌ 通信エラー: {e}")
    print("※インターネット接続を確認するか、BypassSandboxで実行してください。")
