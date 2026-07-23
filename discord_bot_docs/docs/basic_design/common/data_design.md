# データ設計方針

## 方針

| 方針 | 内容 |
|---|---|
| ORM | SQLAlchemy ORM モデルを基準にテーブルを定義する。 |
| 作成 | 起動時に `Base.metadata.create_all` で不足テーブルを作成する。 |
| 移行 | 既存 DB の軽微な差分は `db/schema_migrations.py` で補正する。 |
| 重複防止 | 通知済み状態、source key、unique index で重複通知を抑止する。 |
| 詳細 | テーブル詳細は [テーブル定義書](../../table_definitions/README.md) を参照する。 |

## 主なデータ分類

| 区分 | 主なテーブル |
|---|---|
| メッセージ・ボイスログ | `message_log`, `message_edit_log`, `message_delete_log`, `voice_status_log` |
| AI 分析 | `message_analysis_log`, `message_analysis_feedback`, `communication_trend_analysis` |
| 通知設定 | `b_notify_cannel_config`, `b_niconico_notify_cannel_config` |
| 外部データ | `b_geolonia_address`, `b_geolonia_sync_state`, `b_jma_shindo_station`, `b_jma_sync_state` |
| ICS | `ics_guild_event_config`, `ics_guild_event_import` |
| Niconico | `b_m_niconico_video_infomation`, `b_niconico_video_send_log`, `niconico_info_event`, `niconico_info_filter` |
