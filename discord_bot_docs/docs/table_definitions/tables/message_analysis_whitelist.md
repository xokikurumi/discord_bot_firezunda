# message_analysis_whitelist

## 概要

- テーブル名: `message_analysis_whitelist`
- 分類: ログ
- 説明: Ollama メッセージ分析から除外する guild 単位のホワイトリストルールを保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 3 | `rule_type` | `VARCHAR(30)` | 不可 |  | IDX | `text_exact`、`text_contains`、`user`、`channel` のいずれか。 |
| 4 | `pattern` | `TEXT` | 不可 |  |  | 照合文字列または Discord ID。 |
| 5 | `created_by` | `BIGINT` | 不可 |  | IDX | ルール登録者の Discord ユーザーID。 |
| 6 | `note` | `TEXT` | 可 |  |  | 管理用メモ。 |
| 7 | `enabled` | `BOOLEAN` | 不可 | True | IDX | 有効なルールの場合 true。 |
| 8 | `created_at` | `DATETIME` | 不可 | now() | IDX | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_message_analysis_whitelist_guild_enabled` | いいえ | `guild_id`, `enabled` |
| `idx_message_analysis_whitelist_type_created` | いいえ | `rule_type`, `created_at` |
| `ix_message_analysis_whitelist_created_by` | いいえ | `created_by` |
| `ix_message_analysis_whitelist_guild_id` | いいえ | `guild_id` |

## 備考

- 有効なルールに一致したメッセージは Ollama 分析対象外となり、分析結果は保存されません。
