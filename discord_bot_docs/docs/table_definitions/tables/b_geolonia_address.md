<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# b_geolonia_address

## 概要

- テーブル名: `b_geolonia_address`
- 分類: 基礎データ・設定
- 説明: Geolonia住所データ。住所から緯度・経度を解決するために使用します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `prefecture` | `VARCHAR(50)` | 不可 |  | IDX |  |
| 3 | `municipality` | `VARCHAR(100)` | 不可 |  | IDX |  |
| 4 | `town` | `VARCHAR(150)` | 不可 |  | IDX |  |
| 5 | `lat` | `FLOAT` | 不可 |  |  |  |
| 6 | `lng` | `FLOAT` | 不可 |  |  |  |
| 7 | `source_updated_at` | `DATETIME` | 可 |  |  |  |
| 8 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_geolonia_address` | `UniqueConstraint` | `prefecture`, `municipality`, `town` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_b_geolonia_address_municipality` | いいえ | `municipality` |
| `ix_b_geolonia_address_prefecture` | いいえ | `prefecture` |
| `ix_b_geolonia_address_town` | いいえ | `town` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
