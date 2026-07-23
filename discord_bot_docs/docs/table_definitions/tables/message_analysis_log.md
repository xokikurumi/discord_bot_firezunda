<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# message_analysis_log

## 概要

- テーブル名: `message_analysis_log`
- 分類: ログ
- 説明: Ollamaによるメッセージ解析結果を保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `message_id` | `BIGINT` | 不可 |  | UK | DiscordメッセージID。 |
| 3 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 4 | `channel_id` | `BIGINT` | 不可 |  | IDX | DiscordチャンネルID。 |
| 5 | `user_id` | `BIGINT` | 不可 |  | IDX | DiscordユーザーID、または外部サービスのユーザーID。 |
| 6 | `model` | `VARCHAR(100)` | 不可 |  |  |  |
| 7 | `aggression` | `INTEGER` | 不可 | 0 |  |  |
| 8 | `intimidation` | `INTEGER` | 不可 | 0 |  |  |
| 9 | `insult` | `INTEGER` | 不可 | 0 |  |  |
| 10 | `sarcasm` | `INTEGER` | 不可 | 0 |  |  |
| 11 | `snide` | `INTEGER` | 不可 | 0 |  |  |
| 12 | `discomfort` | `INTEGER` | 不可 | 0 |  |  |
| 13 | `max_score` | `INTEGER` | 不可 | 0 |  |  |
| 14 | `targeted` | `BOOLEAN` | 不可 | True |  | 対象者が明確な投稿かどうか。 |
| 15 | `confidence` | `INTEGER` | 不可 | 100 |  | 分析結果の信頼度。 |
| 16 | `context_dependency` | `BOOLEAN` | 不可 | False |  | 文脈依存または文脈不足があるかどうか。 |
| 17 | `reason` | `TEXT` | 可 |  |  | 分析理由。 |
| 18 | `raw_result` | `TEXT` | 可 |  |  | Ollama 応答を正規化した JSON。 |
| 19 | `prompt_version` | `VARCHAR(100)` | 可 |  |  | 分析に使用したプロンプトバージョン。 |
| 20 | `prompt_hash` | `VARCHAR(64)` | 可 |  |  | 分析に使用したメッセージ配列の SHA-256 ハッシュ。 |
| 21 | `retrieved_rag_cases` | `TEXT` | 可 |  |  | 参照した管理者フィードバック事例の JSON。 |
| 22 | `should_react` | `BOOLEAN` | 不可 | False |  | リアクション付与対象かどうか。 |
| 23 | `should_notify` | `BOOLEAN` | 不可 | False |  | DM 通知対象かどうか。 |
| 24 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `(unnamed)` | `UniqueConstraint` | `message_id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_message_analysis_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_message_analysis_max_score` | いいえ | `max_score`, `created_at` |
| `idx_message_analysis_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_analysis_log_channel_id` | いいえ | `channel_id` |
| `ix_message_analysis_log_guild_id` | いいえ | `guild_id` |
| `ix_message_analysis_log_user_id` | いいえ | `user_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
