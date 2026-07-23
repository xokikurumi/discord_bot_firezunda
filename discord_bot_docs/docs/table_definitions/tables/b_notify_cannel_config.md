<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# b_notify_cannel_config

## 概要

- テーブル名: `b_notify_cannel_config`
- 分類: 基礎データ・設定
- 説明: 通知カテゴリごとの通知先チャンネル設定を管理します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `category` | `VARCHAR(50)` | 不可 |  | IDX |  |
| 3 | `guild_id` | `BIGINT` | 可 |  | IDX | DiscordギルドID。 |
| 4 | `channel_id` | `BIGINT` | 不可 |  |  | DiscordチャンネルID。 |
| 5 | `enabled` | `BOOLEAN` | 不可 | True |  | 有効・無効フラグ。 |
| 6 | `mention` | `TEXT` | 可 |  |  |  |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_b_notify_cannel_config_category` | いいえ | `category` |
| `ix_b_notify_cannel_config_guild_id` | いいえ | `guild_id` |

## 備考

- SQLAlchemyモデル定義から生成しています。DB実体の照合順序・ストレージエンジン等は接続先DBで確認してください。
