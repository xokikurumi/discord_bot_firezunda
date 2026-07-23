<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# b_reaction_keywords

## 概要

- テーブル名: `b_reaction_keywords`
- 分類: 基礎データ・設定
- 説明: キーワードに応じた自動リアクション設定を管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 3 | `enabled` | `BOOLEAN` | 不可 |  |  | 有効・無効フラグ。 |
| 4 | `keyword` | `TEXT` | 不可 |  |  |  |
| 5 | `reaction` | `TEXT` | 可 |  |  |  |
| 6 | `reaction_id` | `BIGINT` | 可 |  |  |  |
| 7 | `reaction_animation_flg` | `BOOLEAN` | 可 |  |  |  |
| 8 | `ng_word_flg` | `BOOLEAN` | 可 |  |  |  |
| 9 | `delete_flg` | `BOOLEAN` | 可 |  |  |  |
| 10 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_b_reaction_keywords_guild_id` | いいえ | `guild_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
