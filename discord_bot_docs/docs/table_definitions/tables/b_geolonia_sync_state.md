<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# b_geolonia_sync_state

## 概要

- テーブル名: `b_geolonia_sync_state`
- 分類: 基礎データ・設定
- 説明: Geolonia住所データ同期状態を管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `name` | `VARCHAR(100)` | 不可 |  |  |  |
| 3 | `last_synced_at` | `DATETIME` | 可 |  |  |  |
| 4 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_geolonia_sync_state_name` | `UniqueConstraint` | `name` |  |

## インデックス

明示的なインデックスはありません。

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
