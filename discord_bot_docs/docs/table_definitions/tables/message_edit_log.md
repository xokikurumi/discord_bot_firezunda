<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# message_edit_log

## 概要

- テーブル名: `message_edit_log`
- 分類: ログ
- 説明: Discordメッセージ編集ログを保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `message_id` | `BIGINT` | 不可 |  | IDX | DiscordメッセージID。 |
| 3 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 4 | `channel_id` | `BIGINT` | 不可 |  | IDX | DiscordチャンネルID。 |
| 5 | `user_id` | `BIGINT` | 不可 |  | IDX | DiscordユーザーID、または外部サービスのユーザーID。 |
| 6 | `before_content` | `TEXT` | 可 |  |  |  |
| 7 | `after_content` | `TEXT` | 可 |  |  |  |
| 8 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_message_edit_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_message_edit_message_created` | いいえ | `message_id`, `created_at` |
| `idx_message_edit_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_edit_log_channel_id` | いいえ | `channel_id` |
| `ix_message_edit_log_guild_id` | いいえ | `guild_id` |
| `ix_message_edit_log_message_id` | いいえ | `message_id` |
| `ix_message_edit_log_user_id` | いいえ | `user_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
