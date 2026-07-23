# message_analysis_feedback

## 概要

- テーブル名: `message_analysis_feedback`
- 分類: ログ
- 説明: Ollamaメッセージ分析に対する管理者フィードバックと補正結果を保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `message_id` | `BIGINT` | 不可 |  | IDX | DiscordメッセージID。 |
| 3 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 4 | `channel_id` | `BIGINT` | 可 |  |  | DiscordチャンネルID。 |
| 5 | `user_id` | `BIGINT` | 可 |  |  | DiscordユーザーID。 |
| 6 | `reviewer_id` | `BIGINT` | 不可 |  | IDX | フィードバック登録者のDiscordユーザーID。 |
| 7 | `label` | `VARCHAR(30)` | 不可 |  |  | `correct`、`false_positive`、`false_negative`、`unsure` のいずれか。 |
| 8 | `review_status` | `VARCHAR(30)` | 不可 | `CONFIRMED` |  | RAG 参照に利用できる確認状態。 |
| 9 | `corrected_result_json` | `TEXT` | 可 |  |  | 管理者確認済みの補正後分析結果JSON。 |
| 10 | `note` | `TEXT` | 可 |  |  | 管理者補足。補正JSONを含められる。 |
| 11 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_message_analysis_feedback_label_created` | いいえ | `label`, `created_at` |
| `idx_message_analysis_feedback_message_created` | いいえ | `message_id`, `created_at` |
| `idx_message_analysis_feedback_status_created` | いいえ | `review_status`, `created_at` |
| `ix_message_analysis_feedback_guild_id` | いいえ | `guild_id` |
| `ix_message_analysis_feedback_message_id` | いいえ | `message_id` |
| `ix_message_analysis_feedback_reviewer_id` | いいえ | `reviewer_id` |

## 備考

- `review_status` が `CONFIRMED` かつ `corrected_result_json` が空でない行は、同一 guild の今後のメッセージ分析で類似事例として参照されます。
