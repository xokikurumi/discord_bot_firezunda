<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# niconico_info_filter

## 概要

- テーブル名: `niconico_info_filter`
- 分類: タスク・通知
- 説明: ニコニコインフォ通知フィルターを管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 3 | `mode` | `VARCHAR(20)` | 不可 | include | IDX |  |
| 4 | `keyword` | `TEXT` | 不可 |  |  |  |
| 5 | `enabled` | `BOOLEAN` | 不可 | True | IDX | 有効・無効フラグ。 |
| 6 | `delete_flg` | `BOOLEAN` | 不可 | False | IDX |  |
| 7 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_niconico_info_filter_delete_flg` | いいえ | `delete_flg` |
| `ix_niconico_info_filter_enabled` | いいえ | `enabled` |
| `ix_niconico_info_filter_guild_id` | いいえ | `guild_id` |
| `ix_niconico_info_filter_mode` | いいえ | `mode` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
