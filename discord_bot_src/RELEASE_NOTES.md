# discord_bot_v3 Release Notes

## 2026-07-11 Public Release

`discord_bot_v3` は、現行稼働版 `discord_bot_firezunda_v2` をもとに、通知機能、ログ機能、Slash Command 対応、Ollama 解析、ニコニコ関連機能を整理・拡張したリリースです。

### v2 からの主な変更

- 起動構成を Cog / Service / Repository / Model に分離しました。
- Prefix Command に加えて Slash Command に対応しました。
- メッセージログをDB中心で保存する構成にしました。
- ニコニコ関連通知を強化しました。
- P2PQuake 通知と地震画像生成を改善しました。
- Ollama によるメッセージ解析結果をDBへ保存するようにしました。
- 半年ごとのユーザ別コミュニケーション傾向分析を追加しました。
- README にセットアップ、設定、各コマンドの使い方を追加しました。

## Added

### Slash Command Support

既存コマンドを Slash Command としても利用できるようにしました。

起動時に以下を実行します。

- Global command sync
- Guild command sync

新しいコマンドが Discord に反映されない場合は、Bot を再起動してください。

### Dice Roll

v2 のダイスロール機能を v3 に追加しました。

利用例:

```text
1d100
2d6+3
!roll 1d20+5
/roll expression:1d20+5
```

### Notification Category List

通知カテゴリ確認用のコマンドを追加しました。

```text
!notify_config category list
/notify_config category list
```

主なカテゴリ:

- `QUAKE`
- `SALES_EVENT`
- `NICONICO_INFO`
- `NICONICO_USER_VIDEO`

### Niconico User Video Notifications

ニコニコ動画のユーザ投稿通知を追加しました。

- 15分ごとに監視します。
- RSS ではなく `nvapi` を使用します。
- ショート動画は `https://www.nicovideo.jp/user/{user_id}/shorts` も確認します。
- ユーザごとに通知先チャンネルを設定できます。
- 送信済み動画は再通知しません。

取得元:

```text
https://nvapi.nicovideo.jp/v2/users/{user_id}/videos
```

設定例:

```text
/niconico_user_video_user add user_id:<user_id>
/niconico_user_video_notify add user_id:<user_id> channel:<channel> mention:<mention>
```

### Niconico Info Notifications

ニコニコインフォ通知を追加しました。

- 1時間ごとに監視します。
- 通知先は `notify_config` の `NICONICO_INFO` カテゴリで設定します。
- include / exclude フィルターに対応しました。
- 通知本文のリンク下に、記事内容の約500文字要約を表示します。
- 送信済み記事は再通知しません。

デフォルトURL:

```text
https://blog.nicovideo.jp/niconews/category/ge_maintenance
https://blog.nicovideo.jp/niconews/category/ge_user/
```

設定例:

```text
/notify_config add channel:<channel> mention:none category:NICONICO_INFO
/niconico_info_filter add keyword:メンテナンス mode:include
/niconico_info_filter add keyword:復旧 mode:exclude
```

### Message Sticker Logging

`message_log` にスタンプ情報を保存するようにしました。

追加項目:

- `has_stickers`
- `stickers`

### Ollama Message Analysis Log

Ollama によるメッセージ解析結果を `message_analysis_log` に保存するようにしました。

保存内容:

- Discord message id
- guild id
- channel id
- user id
- 使用モデル
- 各スコア
- 最大スコア
- 理由
- raw JSON
- リアクション対象判定
- DM通知対象判定

### Semiannual Communication Trend Analysis

半年ごとのコミュニケーション傾向分析を追加しました。

- `message_log`
- `message_delete_log`
- `message_edit_log`
- `message_analysis_log`

上記をもとに、ユーザごとの傾向を Ollama で解析します。

基本方針:

- ユーザ単位で解析します。
- 同じユーザが複数ギルドにいる場合は、ギルドごとに別レポートを作成します。
- 保存先は `communication_trend_analysis` です。
- デフォルトではギルド全体レポートは作成しません。
- 自動実行日は日本時間の 1月1日 と 6月1日 です。
- 解析結果はチャットへ投稿せず、内部管理/監視用として保存します。

手動実行:

```text
!communication_trend_analyze
/communication_trend_analyze
```

### ICS Scheduled Event Import

ICS をもとに Discord のスケジュールイベントを作成する機能を追加しました。

通知先は `notify_config` の `SALES_EVENT` カテゴリで設定します。

## Changed

### Niconico User Video Fetch

v2 では DB キューや RSS ベースの経路がありましたが、v3 では `nvapi` を直接使用します。

ユーザ動画投稿通知の実行タイミングを、起動時刻からの15分間隔ではなく毎時 `00` / `15` / `30` / `45` 分に固定しました。

通知本文の投稿時間は、APIの日時を日本時間へ変換して `yyyy/mm/dd hh:mm:ss` 形式で表示します。

これにより、以下のような RSS 由来の問題を回避します。

```text
undefined entity
Niconico RSS endpoint returned non-RSS content
```

### Niconico Info Fetch

v2 では `browser_send` テーブルに入った内容を通知する構成でした。

v3 では、Bot 側で対象URLを取得し、`niconico_info_event` に保存して通知します。

外部バッチが引き続き `browser_send` に書き込む運用の場合、そのデータは v3 のニコニコインフォ通知では使用されません。

### Earthquake Image

地震画像の表示を調整しました。

- 震源地記号を `✖` に変更
- 発生時刻の日付と時刻を改行表示に変更
- 観測地点検索で市町村名抽出に対応
- 地図上に観測地点のプロットと地点名ラベルを表示
- 最大震度1の地震でも観測地点を表示対象に変更
- 国土地理院タイルを `GSI_TILE_CACHE_DIR` 配下に保存し、同じタイルはローカルから再利用

### P2PQuake WebSocket Watcher

WebSocket監視タスク自体が停止した場合に、`P2PQUAKE_RECONNECT_DELAY` 秒後に自動で再起動するようにしました。

例:

```text
魚沼市今泉 -> 魚沼市
```

### Communication Trend Analysis

初期実装ではギルド全体レポートも作成していましたが、公開版ではユーザ単位を基本にしました。

ギルド全体レポートが必要な場合は以下を設定します。

```text
COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED=true
```

## Fixed

- ニコニコ RSS の非RSS応答や XML entity 問題を回避しました。
- Slash Command が反映されにくい問題に対応するため guild sync を追加しました。
- Ollama 半期分析の空応答時にリトライするようにしました。
- Ollama 半期分析で配列が返った場合に DB 保存エラーになる問題を修正しました。
- 半期分析の失敗レコードは再実行時に更新されるようにしました。
- 半期分析の自動実行日を 1月1日 / 6月1日 に変更しました。

## Database Changes

主な追加・変更テーブル:

- `message_log`
  - `message_created_at`
  - `has_stickers`
  - `stickers`

- `message_analysis_log`
  - Ollama のメッセージ解析結果を保存します。

- `communication_trend_analysis`
  - 半年ごとのユーザ別コミュニケーション傾向分析を保存します。

- `b_m_niconico_video_infomation`
  - ニコニコ投稿監視対象ユーザを保存します。

- `b_niconico_notify_cannel_config`
  - ニコニコユーザごとの通知先を保存します。

- `b_niconico_video_send_log`
  - ニコニコ投稿通知の重複防止に使用します。

- `niconico_info_event`
  - ニコニコインフォ通知対象記事を保存します。

- `niconico_info_filter`
  - ニコニコインフォ通知の include / exclude フィルターを保存します。

## Configuration

主な追加設定:

```text
SLASH_COMMAND_SYNC_TO_GUILDS=true

NICONICO_USER_VIDEO_ENABLED=true

NICONICO_INFO_ENABLED=true
NICONICO_INFO_CHECK_INTERVAL_SECONDS=3600
NICONICO_INFO_TARGET_URLS=...

COMMUNICATION_TREND_ANALYSIS_ENABLED=true
COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED=false
COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS=86400
COMMUNICATION_TREND_MIN_USER_MESSAGES=1
COMMUNICATION_TREND_SAMPLE_LIMIT=30
COMMUNICATION_TREND_NUM_PREDICT=2048
```

## Commands

詳細な使い方は `README.md` を参照してください。

主な追加コマンド:

```text
/roll
/notify_config category list
/niconico_user_video_user add
/niconico_user_video_notify add
/niconico_info_check
/niconico_info_filter add
/communication_trend_analyze
```

## Compatibility Notes

v2 と完全に同じDBキューを読むわけではありません。

特に以下は v3 で方式が変わっています。

- `browser_send`
  - v3 のニコニコインフォ通知では使用しません。

- `B_SALES_EVENT`
  - v3 では ICS 取り込みベースです。

- `B_DISASTER_INFOMATION`
  - v3 では P2PQuake 通知が中心です。

- ギルド全体の半期分析
  - デフォルトでは作成しません。
  - ユーザ単位分析を基本にしています。

## Operational Notes

- Bot 初回起動時にDBテーブル作成と軽量マイグレーションを実行します。
- Slash Command が見えない場合は Bot を再起動してください。
- ニコニコユーザ投稿通知は、監視対象ユーザと通知先の両方を設定してください。
- 既に失敗した半期分析レコードは `/communication_trend_analyze` で再実行すると更新されます。
- 半期分析の結果本文はチャットへ投稿されません。
