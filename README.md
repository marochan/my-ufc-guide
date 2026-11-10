# UFC 334 完全徹底解剖観戦ガイド（Web Magazine）

![GitHub Pages Deployment](https://img.shields.io/badge/GitHub%20Pages-Live%20Deploy-success?style=for-the-badge&logo=github)
![Data Source](https://img.shields.io/badge/Data%20Source-ESPN%20MMA%20API%20%7C%20DraftKings%20%7C%20Tapology-blue?style=for-the-badge)
![Volume](https://img.shields.io/badge/Volume-13%20Bouts%20%2F%20170k%20Characters-red?style=for-the-badge)

UFC 334 マディソン・スクエア・ガーデン（MSG）大会の全13試合を網羅した、完全事実ベースの超リッチWebマガジン形式観戦ガイドです。

🌐 **公開Webサイト（GitHub Pages）**:  
👉 **[https://marochan.github.io/my-ufc-guide/](https://marochan.github.io/my-ufc-guide/)**

---

## 🌟 主な特徴・機能

1. **完全な事実ベース・大長文統合（約17万文字 / 260KB）**:
   - 初稿の選手のディープな生い立ち・技術戦術分析・Reddit海外コミュニティ反応を一切要約・省略せずに収録。
   - 情報の引用元（ESPN、UFC公式、DraftKings、Tapology、Covers等）を各データの直後に配置。
2. **全26選手の公式データ完全網羅**:
   - **ESPN公式高画質顔写真 ＆ 国旗アイコン**: 全26選手を表示。
   - **確定戦績バッジ ＆ 公式年齢・生年月日**: 各選手カードのヘッダーに配置。
   - **直近3試合公式戦績ブロック**: 勝敗（WIN/LOSS/NC）・対戦相手・決着方法・大会名・日付を完全表示。
   - **ESPN公式Fight History直接リンク**: 3試合より前の過去全対戦履歴へ直接アクセス可能。
   - **選手プロフィール＆データ詳細テーブル**: 全13試合の選手カード上部に横幅100%全幅で配置。
3. **最新確定オッズ ＆ 3大BET予想サイト コンセンサス比較**:
   - 最新マネーラインオッズ（DraftKings / Bet365）。
   - **Tapology**（ファン投票）、**Covers**（専門家分析）、**DraftKings**（プロップ市場）の4大指標横並び比較テーブル（①予想勝者、②決着方法、③決着ラウンド、④判定種別［3-0ユナニマスか2-1スプリットか］）。
4. **時系列降順レイアウト（メイン上・オープニング下）**:
   - 読者の注目度が高いメインイベント（シリル・ガーヌ vs ジョシュ・ホキット）を最上部に、大会オープニングマッチ（ジャレッド・ゴードン vs メルキザエル・コスタ）を最下部に配置。
5. **インタラクティブ機能**:
   - 目次内のリアルタイム選手・階級検索バー ＆ カテゴリ絞り込みタブ。
   - スクロール追従フローティングアクションボタン（📑目次 / ▲TOPへ戻る）。
   - 読者参加型「My予想チェッカー」（LocalStorage自動保存・進捗バー・Xシェアボタン）。
   - 日本時間（JST）＆現地時間（EST）対照タイムスケジュール表。
   - 印刷・PDF保存用Print CSS（白背景・インク節約自動最適化）。
6. **大会直前ステータス速報 ＆ 公式差分チェッカー**:
   - 大会概要冒頭の「⚡ Live Card Updates」速報バナー。
   - 各試合ヘッダーの「公式ステータスバッジ（カード確定 / 代打スクランブル参戦）」。

---

## 🛠️ 大会直前・公式対戦カード差分チェッカー

大会直前の選手の負傷欠場・代打参戦・試合中止がないかを、ESPN公式API（一次情報DB）と突き合わせてワンクリックで自動検知できます。

### 実行方法
```powershell
python check_ufc334_status.py
```

### 実行例
```text
📡 取得イベント: UFC 334: Gane vs. Hokit (2026-11-14T22:00Z)
📊 ESPN公式登録試合数: 13 試合
📄 本サイト掲載試合数: 13 試合

【全試合ステータス照合結果】
  ✅ 第1戦: Ciryl Gane vs Josh Hokit -> [正常一致 / STATUS_SCHEDULED]
  ✅ 第2戦: Kayla Harrison vs Amanda Nunes -> [正常一致 / STATUS_SCHEDULED]
  ...
🎉 【公式確認完了】全13試合すべてESPN公式データと照合確認済みです。
   急な試合中止（Cancelled）は発生していません。
```

---

## 📁 ディレクトリ構成

```text
my-ufc-guide/
├── index.html                  # 観戦ガイド本体（レスポンシブWebマガジン）
├── check_ufc334_status.py      # ESPN公式対戦カード差分チェッカー
├── .nojekyll                   # GitHub Pages ビルドバイパス設定
├── .gitignore                  # 作業記録(work_records/)および元原稿(ufc/)の除外設定
├── README.md                   # プロジェクト概要・ドキュメント（本ファイル）
└── work_records/               # ローカル作業記録（NotebookLM連携用、Git管理除外）
```

---

## 📜 ライセンス・データ帰属
- データソース: ESPN MMA API, UFC Official Athlete Profiles, DraftKings Sportsbook, Bet365, Tapology, Covers.
- コミュニティ反応: Reddit (/r/mma, /r/ufc).
