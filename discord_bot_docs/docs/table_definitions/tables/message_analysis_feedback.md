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
| 8 | `reason_tag` | `VARCHAR(50)` | 可 |  | IDX | フィードバック理由タグ。 |
| 9 | `review_status` | `VARCHAR(30)` | 不可 | `CONFIRMED` |  | RAG 参照に利用できる確認状態。 |
| 10 | `corrected_result_json` | `TEXT` | 可 |  |  | 管理者確認済みの補正後分析結果JSON。 |
| 11 | `note` | `TEXT` | 可 |  |  | 管理者補足。補正JSONを含められる。 |
| 12 | `embedding_model` | `VARCHAR(100)` | 可 |  | IDX | feedback embedding を作成した Ollama embedding model。 |
| 13 | `embedding_text_hash` | `VARCHAR(64)` | 可 |  | IDX | embedding 入力文字列の SHA-256 hash。 |
| 14 | `embedding_dim` | `INTEGER` | 可 |  |  | embedding vector の次元数。 |
| 15 | `embedding_json` | `TEXT` | 可 |  |  | embedding vector を JSON 配列として保存した値。 |
| 16 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_message_analysis_feedback_label_created` | いいえ | `label`, `created_at` |
| `idx_message_analysis_feedback_message_created` | いいえ | `message_id`, `created_at` |
| `idx_message_analysis_feedback_reason_tag_created` | いいえ | `reason_tag`, `created_at` |
| `idx_message_analysis_feedback_status_created` | いいえ | `review_status`, `created_at` |
| `idx_message_analysis_feedback_embedding` | いいえ | `embedding_model`, `embedding_text_hash` |
| `ix_message_analysis_feedback_guild_id` | いいえ | `guild_id` |
| `ix_message_analysis_feedback_message_id` | いいえ | `message_id` |
| `ix_message_analysis_feedback_reviewer_id` | いいえ | `reviewer_id` |

## 備考

- `review_status` が `CONFIRMED` かつ `corrected_result_json` が空でない行は、同一 guild の今後のメッセージ分析で類似事例として参照されます。
- `label` と `reason_tag` は Discord の slash command では日本語補足付きで表示されますが、保存値は英語 ID です。
- embedding 列が保存されている場合、語彙類似度に加えて embedding 類似度による RAG 候補評価に使用されます。
- embedding 入力文字列には対象本文、label、reason tag、note を含めます。
