# DB 初期化・スキーマ移行詳細

## 1. 目的

Bot 起動時に不足テーブルを作成し、既存環境の軽微なスキーマ差分を破壊的でない範囲で補正する。

## 2. DB 接続

| 項目 | 仕様 |
|---|---|
| engine | SQLAlchemy async engine |
| session | `AsyncSession` |
| session option | `expire_on_commit=False` |
| pool size | `10` |
| max overflow | `20` |
| pool pre ping | 有効 |
| echo | 無効 |

DB URL は環境変数 `DB_URL` があればそれを優先し、なければ user/password/host/port/name から MySQL aiomysql URL を組み立てる。

## 3. 初期化処理

1. engine の begin transaction を開く。
2. ORM metadata の `create_all` を実行し、不足テーブルを作成する。
3. 軽量マイグレーションを実行する。
4. 完了ログを出力する。

## 4. 軽量マイグレーション

`create_all` は既存テーブルの変更を行わないため、次の補正を情報スキーマ確認後に idempotent に実行する。

| 対象 | 処理 |
|---|---|
| message_edit_log / message_delete_log | `message_id` に存在する legacy unique index を削除する |
| message_log | `message_created_at`、`has_stickers`、`stickers` を追加する |
| discord_user | guild/user 基本属性と `last_seen_at` を追加する |
| discord_channel | channel 基本属性と `last_seen_at` を追加する |
| message_edit_log | `guild_id`、`channel_id`、`user_id` を追加する |
| message_delete_log | guild/channel/user/content/添付/埋め込み関連列を追加する |
| message_analysis_log | Ollama 分析スコア、判定、raw result、prompt version、prompt hash、参照 RAG 事例を追加する |
| message_analysis_feedback | 管理者フィードバック、review status、補正結果 JSON を追加する |
| communication_trend_analysis | 半期分析結果列を追加する |
| b_niconico_video_send_log | 投稿日、送信済み、削除フラグ、作成日時を追加する |
| b_m_niconico_video_infomation | 削除フラグを追加する |
| b_niconico_notify_cannel_config | 有効フラグ、メンションを追加する |
| niconico_info_event | Niconico Info 検出イベント列を追加する |
| niconico_info_filter | guild 別フィルタ列を追加する |

## 5. unique index 作成

次の index が存在しない場合のみ作成する。

| index | 対象 |
|---|---|
| `uq_ics_guild_event_import_guild_uid` | `ics_guild_event_import(guild_id, ics_uid)` |
| `uq_niconico_info_event_source_key` | `niconico_info_event(source_key)` |
| `uq_message_analysis_log_message_id` | `message_analysis_log(message_id)` |
| `uq_discord_user_guild_user` | `discord_user(guild_id, user_id)` |
| `uq_discord_channel_guild_channel` | `discord_channel(guild_id, channel_id)` |

## 6. 単体実行用操作

開発用に、全テーブル作成、全テーブル削除、全テーブル再作成、`SELECT 1` による接続確認を提供する。通常起動では削除系は使用しない。
