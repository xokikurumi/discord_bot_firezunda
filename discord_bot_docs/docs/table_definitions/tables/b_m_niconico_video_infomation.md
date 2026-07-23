<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# b_m_niconico_video_infomation

## 概要

- テーブル名: `b_m_niconico_video_infomation`
- 分類: タスク・通知
- 説明: ニコニコ動画ユーザー投稿通知の監視対象ユーザーを管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `user_id` | `BIGINT` | 不可 |  | IDX | DiscordユーザーID、または外部サービスのユーザーID。 |
| 3 | `delete_flg` | `BOOLEAN` | 不可 | False | IDX |  |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_b_m_niconico_video_infomation_delete_flg` | いいえ | `delete_flg` |
| `ix_b_m_niconico_video_infomation_user_id` | いいえ | `user_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
