<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# b_jma_shindo_station

## 概要

- テーブル名: `b_jma_shindo_station`
- 分類: 基礎データ・設定
- 説明: 気象庁震度観測点データ。観測地点の住所・緯度・経度を管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `region_name` | `VARCHAR(100)` | 不可 |  | IDX |  |
| 3 | `station_name` | `VARCHAR(150)` | 不可 |  | IDX |  |
| 4 | `address` | `TEXT` | 可 |  |  |  |
| 5 | `lat` | `FLOAT` | 不可 |  |  |  |
| 6 | `lng` | `FLOAT` | 不可 |  |  |  |
| 7 | `observation_start` | `VARCHAR(20)` | 可 |  |  |  |
| 8 | `observation_end` | `VARCHAR(20)` | 可 |  | IDX |  |
| 9 | `source_updated_at` | `DATETIME` | 可 |  |  |  |
| 10 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_jma_shindo_station_name_lat_lng` | `UniqueConstraint` | `station_name`, `lat`, `lng` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_b_jma_shindo_station_observation_end` | いいえ | `observation_end` |
| `ix_b_jma_shindo_station_region_name` | いいえ | `region_name` |
| `ix_b_jma_shindo_station_station_name` | いいえ | `station_name` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
