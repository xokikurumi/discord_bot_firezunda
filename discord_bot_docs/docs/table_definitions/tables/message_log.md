<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# message_log

## 概要

- テーブル名: `message_log`
- 分類: ログ
- 説明: Discordメッセージ投稿ログを保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `message_id` | `BIGINT` | 不可 |  | UK | DiscordメッセージID。 |
| 3 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 4 | `channel_id` | `BIGINT` | 不可 |  | IDX | DiscordチャンネルID。 |
| 5 | `user_id` | `BIGINT` | 不可 |  | IDX | DiscordユーザーID、または外部サービスのユーザーID。 |
| 6 | `bot_flg` | `BOOLEAN` | 不可 |  |  |  |
| 7 | `content` | `TEXT` | 可 |  |  |  |
| 8 | `message_created_at` | `DATETIME` | 可 |  | IDX |  |
| 9 | `has_attachments` | `BOOLEAN` | 不可 | False |  |  |
| 10 | `has_embeds` | `BOOLEAN` | 不可 | False |  |  |
| 11 | `has_stickers` | `BOOLEAN` | 不可 | False |  |  |
| 12 | `stickers` | `TEXT` | 可 |  |  |  |
| 13 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `(unnamed)` | `UniqueConstraint` | `message_id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_channel_message_created` | いいえ | `channel_id`, `message_created_at` |
| `idx_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_log_channel_id` | いいえ | `channel_id` |
| `ix_message_log_guild_id` | いいえ | `guild_id` |
| `ix_message_log_message_created_at` | いいえ | `message_created_at` |
| `ix_message_log_user_id` | いいえ | `user_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
