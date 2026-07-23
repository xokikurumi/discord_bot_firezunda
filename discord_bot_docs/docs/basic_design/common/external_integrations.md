# 外部連携設計

| 連携先 | 用途 | 主な設定 |
|---|---|---|
| Discord API | Bot 接続、コマンド、イベント、通知投稿、予定イベント作成 | `DISCORD_TOKEN` |
| MySQL | 永続化 | `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` |
| Ollama | メッセージ分析、管理者フィードバック事例を含む分析補正、傾向分析レポート生成 | `OLLAMA_URL`, `OLLAMA_MODEL` |
| P2PQuake | 地震・津波・EEW イベント受信 | `P2PQUAKE_WS_URL` |
| GSI | 地図タイル取得 | `GSI_BLANK_TILE_BASE_URL`, `GSI_TILE_CACHE_DIR` |
| Geolonia | 住所データ取得 | `GEOLONIA_JAPANESE_ADDRESSES_API_BASE_URL` |
| 気象庁 | 震度観測点取得 | `JMA_SHINDO_STATION_URL` |
| ICS URL | Discord 予定イベント取り込み | `ICS_GUILD_EVENT_URL` |
| Niconico | 動画投稿・Info 記事取得 | `NICONICO_INFO_TARGET_URLS` |

## 共通方針

- 外部接続失敗時は例外を捕捉し、Bot 全体の停止を避ける。
- 定期処理は次回実行で再試行できる状態を維持する。
- 外部 API の URL や有効化フラグは環境変数で変更可能にする。
