# discord_user

## 概要

- テーブル名: `discord_user`
- 分類: 基礎データ・設定
- 説明: メッセージログで観測した Discord ユーザーの最新属性を保持します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `guild_id` | `BIGINT` | 不可 |  | UK/IDX | DiscordギルドID。 |
| 3 | `user_id` | `BIGINT` | 不可 |  | UK/IDX | DiscordユーザーID。 |
| 4 | `name` | `VARCHAR(100)` | 可 |  |  | ユーザー名。 |
| 5 | `display_name` | `VARCHAR(100)` | 可 |  |  | サーバー内表示名。 |
| 6 | `global_name` | `VARCHAR(100)` | 可 |  |  | グローバル表示名。 |
| 7 | `discriminator` | `VARCHAR(10)` | 可 |  |  | Discord discriminator。 |
| 8 | `bot_flg` | `BOOLEAN` | 不可 | False |  | Bot ユーザーの場合 true。 |
| 9 | `avatar_url` | `VARCHAR(500)` | 可 |  |  | 表示 avatar URL。 |
| 10 | `last_seen_at` | `DATETIME` | 可 |  | IDX | 最後にメッセージで観測した日時。 |
| 11 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_discord_user_guild_user` | `Unique Index` | `guild_id`, `user_id` | 同一 guild 内の同一 user を一意にする。 |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_discord_user_last_seen` | いいえ | `guild_id`, `last_seen_at` |
| `ix_discord_user_guild_id` | いいえ | `guild_id` |
| `ix_discord_user_user_id` | いいえ | `user_id` |

## 備考

- メッセージ作成または履歴取り込み時に、投稿者の最新情報で upsert されます。
