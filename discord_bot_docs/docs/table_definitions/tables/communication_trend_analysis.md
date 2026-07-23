<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# communication_trend_analysis

## 概要

- テーブル名: `communication_trend_analysis`
- 分類: ログ
- 説明: 半期ごとのコミュニケーション傾向分析結果を保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `period_key` | `VARCHAR(20)` | 不可 |  | IDX |  |
| 3 | `period_start` | `DATETIME` | 不可 |  |  |  |
| 4 | `period_end` | `DATETIME` | 不可 |  |  |  |
| 5 | `scope_type` | `VARCHAR(20)` | 不可 |  | IDX |  |
| 6 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 7 | `user_id` | `BIGINT` | 可 |  | IDX | DiscordユーザーID、または外部サービスのユーザーID。 |
| 8 | `model` | `VARCHAR(100)` | 不可 |  |  |  |
| 9 | `message_count` | `INTEGER` | 不可 | 0 |  |  |
| 10 | `edit_count` | `INTEGER` | 不可 | 0 |  |  |
| 11 | `delete_count` | `INTEGER` | 不可 | 0 |  |  |
| 12 | `analysis_count` | `INTEGER` | 不可 | 0 |  |  |
| 13 | `max_score_avg` | `INTEGER` | 不可 | 0 |  |  |
| 14 | `metrics` | `TEXT` | 可 |  |  |  |
| 15 | `summary` | `TEXT` | 可 |  |  |  |
| 16 | `tendencies` | `TEXT` | 可 |  |  |  |
| 17 | `risks` | `TEXT` | 可 |  |  |  |
| 18 | `recommendations` | `TEXT` | 可 |  |  |  |
| 19 | `raw_result` | `TEXT` | 可 |  |  |  |
| 20 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `idx_comm_trend_guild_created` | いいえ | `guild_id`, `created_at` |
| `idx_comm_trend_period_scope` | いいえ | `period_key`, `scope_type`, `guild_id`, `user_id` |
| `idx_comm_trend_user_created` | いいえ | `user_id`, `created_at` |
| `ix_communication_trend_analysis_guild_id` | いいえ | `guild_id` |
| `ix_communication_trend_analysis_period_key` | いいえ | `period_key` |
| `ix_communication_trend_analysis_scope_type` | いいえ | `scope_type` |
| `ix_communication_trend_analysis_user_id` | いいえ | `user_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
