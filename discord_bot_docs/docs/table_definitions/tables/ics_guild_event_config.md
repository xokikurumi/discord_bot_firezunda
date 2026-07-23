<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# ics_guild_event_config

## 概要

- テーブル名: `ics_guild_event_config`
- 分類: タスク・通知
- 説明: ICS予定イベント取り込みのギルド別有効・無効設定を管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `guild_id` | `BIGINT` | 不可 |  | IDX | DiscordギルドID。 |
| 3 | `enabled` | `BOOLEAN` | 不可 | False<br>0 |  | 有効・無効フラグ。 |
| 4 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_ics_guild_event_config_guild_id` | `UniqueConstraint` | `guild_id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_ics_guild_event_config_guild_id` | いいえ | `guild_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
