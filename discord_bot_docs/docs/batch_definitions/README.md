# バッチ処理定義一覧

## 1. 概要

Bot 起動後にバックグラウンドで実行される処理、イベントを契機に非同期実行される処理、および運用者が必要に応じて実行する処理を定義する。

## 2. バッチ処理一覧

| ID | 処理名 | 実行方式 | 起動契機 | 詳細 |
|---|---|---|---|---|
| BATCH-001 | DB 初期化・軽量マイグレーション | 起動時処理 | Bot 起動時 | [詳細](batches/database_startup_migration.md) |
| BATCH-002 | P2PQuake WebSocket 監視 | 常駐監視 | Bot 起動時 | [詳細](batches/p2pquake_websocket_watch.md) |
| BATCH-003 | JMA 震度観測点同期 | 定期処理 | P2PQuake 監視開始時 | [詳細](batches/jma_shindo_station_sync.md) |
| BATCH-004 | ICS 予定イベント取り込み | 定期処理・手動実行 | Bot 起動時、コマンド実行時 | [詳細](batches/ics_guild_event_import.md) |
| BATCH-005 | コミュニケーション傾向分析 | 定期処理・手動実行 | Bot 起動時、コマンド実行時 | [詳細](batches/communication_trend_analysis.md) |
| BATCH-006 | Niconico Info 確認・通知 | 定期処理・手動実行 | Bot 起動時、コマンド実行時 | [詳細](batches/niconico_info_check.md) |
| BATCH-007 | Niconico ユーザー投稿動画確認・通知 | 定期処理・手動実行 | Bot 起動時、コマンド実行時 | [詳細](batches/niconico_user_video_check.md) |
| BATCH-008 | Ollama メッセージ分析 | イベント駆動非同期処理 | メッセージ投稿時 | [詳細](batches/ollama_message_analysis.md) |
| BATCH-009 | GSI タイル事前キャッシュ | 手動スクリプト | 運用者実行 | [詳細](batches/gsi_tile_cache.md) |
| BATCH-010 | リリース切り替え | 手動スクリプト | 運用者実行 | [詳細](batches/release_switch.md) |
| BATCH-011 | DB テーブル定義生成 | 手動スクリプト | 開発・保守時 | [詳細](batches/db_table_definition_generation.md) |
| BATCH-012 | DB 初期化スクリプト | 手動スクリプト | 開発・保守時 | [詳細](batches/db_init_script.md) |
| BATCH-013 | Geolonia 住所同期 | 定期処理 | P2PQuake 監視開始時 | [詳細](batches/geolonia_address_sync.md) |

## 3. 実行分類

| 分類 | 説明 |
|---|---|
| 起動時処理 | Bot 起動シーケンス内で実行される処理 |
| 常駐監視 | WebSocket などに接続し続け、切断時に再接続する処理 |
| 定期処理 | 一定間隔または予定日に繰り返し実行される処理 |
| イベント駆動非同期処理 | Discord イベントを契機に非同期実行される処理 |
| 手動スクリプト | 運用者または CI/CD が明示的に実行する処理 |

## 4. 関連設定

| 設定 | 主な利用処理 |
|---|---|
| `DISCORD_TOKEN` | Bot 起動 |
| `DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`、`DB_NAME` | DB 接続を伴う全処理 |
| `P2PQUAKE_ENABLED` | P2PQuake WebSocket 監視 |
| `JMA_SHINDO_STATION_SYNC_ENABLED` | JMA 震度観測点同期 |
| `GEOLONIA_ADDRESS_SYNC_ENABLED` | Geolonia 住所同期 |
| `ICS_GUILD_EVENT_ENABLED` | ICS 予定イベント取り込み |
| `COMMUNICATION_TREND_ANALYSIS_ENABLED` | コミュニケーション傾向分析 |
| `OLLAMA_ANALYSIS_ENABLED` | Ollama メッセージ分析 |
| `NICONICO_INFO_ENABLED` | Niconico Info 確認・通知 |
| `NICONICO_USER_VIDEO_ENABLED` | Niconico ユーザー投稿動画確認・通知 |
