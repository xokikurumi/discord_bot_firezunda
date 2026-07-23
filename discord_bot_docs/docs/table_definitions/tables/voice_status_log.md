<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# voice_status_log

## 概要

- テーブル名: `voice_status_log`
- 分類: ログ
- 説明: Discordボイスチャンネル状態変更ログを保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `before_guild_id` | `BIGINT` | 不可 |  | IDX |  |
| 3 | `after_guild_id` | `BIGINT` | 不可 |  | IDX |  |
| 4 | `user_id` | `BIGINT` | 不可 |  | IDX | DiscordユーザーID、または外部サービスのユーザーID。 |
| 5 | `before_channel_id` | `BIGINT` | 可 |  | IDX |  |
| 6 | `after_channel_id` | `BIGINT` | 可 |  | IDX |  |
| 7 | `before_mute` | `BOOLEAN` | 可 |  | IDX |  |
| 8 | `after_mute` | `BOOLEAN` | 可 |  | IDX |  |
| 9 | `before_deaf` | `BOOLEAN` | 可 |  | IDX |  |
| 10 | `after_deaf` | `BOOLEAN` | 可 |  | IDX |  |
| 11 | `before_video` | `BOOLEAN` | 可 |  | IDX |  |
| 12 | `after_video` | `BOOLEAN` | 可 |  | IDX |  |
| 13 | `before_stream` | `BOOLEAN` | 可 |  | IDX |  |
| 14 | `after_stream` | `BOOLEAN` | 可 |  | IDX |  |
| 15 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_after_channel_created` | いいえ | `after_channel_id`, `created_at` |
| `idx_before_channel_created` | いいえ | `before_channel_id`, `created_at` |
| `idx_user_created` | いいえ | `user_id`, `created_at` |
| `ix_voice_status_log_after_channel_id` | いいえ | `after_channel_id` |
| `ix_voice_status_log_after_deaf` | いいえ | `after_deaf` |
| `ix_voice_status_log_after_guild_id` | いいえ | `after_guild_id` |
| `ix_voice_status_log_after_mute` | いいえ | `after_mute` |
| `ix_voice_status_log_after_stream` | いいえ | `after_stream` |
| `ix_voice_status_log_after_video` | いいえ | `after_video` |
| `ix_voice_status_log_before_channel_id` | いいえ | `before_channel_id` |
| `ix_voice_status_log_before_deaf` | いいえ | `before_deaf` |
| `ix_voice_status_log_before_guild_id` | いいえ | `before_guild_id` |
| `ix_voice_status_log_before_mute` | いいえ | `before_mute` |
| `ix_voice_status_log_before_stream` | いいえ | `before_stream` |
| `ix_voice_status_log_before_video` | いいえ | `before_video` |
| `ix_voice_status_log_user_id` | いいえ | `user_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
