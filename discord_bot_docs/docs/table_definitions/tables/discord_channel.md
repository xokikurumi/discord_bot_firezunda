# discord_channel

## 概要

- テーブル名: `discord_channel`
- 分類: 基礎データ・設定
- 説明: メッセージログで観測した Discord チャンネルの最新属性を保持します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `guild_id` | `BIGINT` | 不可 |  | UK/IDX | DiscordギルドID。 |
| 3 | `channel_id` | `BIGINT` | 不可 |  | UK/IDX | DiscordチャンネルID。 |
| 4 | `name` | `VARCHAR(100)` | 可 |  |  | チャンネル名。 |
| 5 | `channel_type` | `VARCHAR(50)` | 可 |  |  | チャンネル種別。 |
| 6 | `category_id` | `BIGINT` | 可 |  |  | カテゴリID。 |
| 7 | `parent_channel_id` | `BIGINT` | 可 |  |  | 親チャンネルID。 |
| 8 | `position` | `INTEGER` | 可 |  |  | 表示順。 |
| 9 | `last_seen_at` | `DATETIME` | 可 |  | IDX | 最後にメッセージで観測した日時。 |
| 10 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_discord_channel_guild_channel` | `Unique Index` | `guild_id`, `channel_id` | 同一 guild 内の同一 channel を一意にする。 |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_discord_channel_last_seen` | いいえ | `guild_id`, `last_seen_at` |
| `ix_discord_channel_channel_id` | いいえ | `channel_id` |
| `ix_discord_channel_guild_id` | いいえ | `guild_id` |

## 備考

- メッセージ作成または履歴取り込み時に、投稿チャンネルの最新情報で upsert されます。
