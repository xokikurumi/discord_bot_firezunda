<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# niconico_info_event

## 概要

- テーブル名: `niconico_info_event`
- 分類: タスク・通知
- 説明: ニコニコインフォ通知対象記事と送信状態を管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `source_key` | `VARCHAR(255)` | 不可 |  | UK<br>IDX |  |
| 3 | `title` | `TEXT` | 不可 |  |  |  |
| 4 | `start_date` | `DATE` | 可 |  |  |  |
| 5 | `end_date` | `DATE` | 可 |  |  |  |
| 6 | `date_text` | `TEXT` | 可 |  |  |  |
| 7 | `explanation` | `TEXT` | 可 |  |  |  |
| 8 | `link` | `TEXT` | 可 |  |  |  |
| 9 | `organizer_user` | `TEXT` | 可 |  |  |  |
| 10 | `organizer_link` | `TEXT` | 可 |  |  |  |
| 11 | `categories` | `TEXT` | 可 |  |  |  |
| 12 | `source_url` | `TEXT` | 可 |  |  |  |
| 13 | `send_flg` | `BOOLEAN` | 不可 | False | IDX |  |
| 14 | `delete_flg` | `BOOLEAN` | 不可 | False | IDX |  |
| 15 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_niconico_info_event_delete_flg` | いいえ | `delete_flg` |
| `ix_niconico_info_event_send_flg` | いいえ | `send_flg` |
| `ix_niconico_info_event_source_key` | はい | `source_key` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
