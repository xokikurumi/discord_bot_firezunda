# DB 初期化・軽量マイグレーション

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-001 |
| 処理名 | DB 初期化・軽量マイグレーション |
| 実装 | `main.py`、`db/schema_migrations.py` |
| 実行方式 | Bot 起動時処理 |
| 起動契機 | `python main.py` 実行時 |

## 2. 処理概要

Bot 起動時に ORM 定義から不足テーブルを作成し、既存環境との差分を補正する軽量マイグレーションを実行します。

## 3. 処理詳細

1. `Base.metadata.create_all` で存在しないテーブルを作成する。
2. `run_schema_migrations` を実行する。
3. 既存テーブルの不足カラムを追加する。
4. 一部の重複防止 index を作成する。
5. 旧仕様の不要な unique index を削除する。

## 4. 主な対象テーブル

| 種別 | テーブル |
|---|---|
| メッセージログ | `message_log`、`message_edit_log`、`message_delete_log` |
| 分析ログ | `message_analysis_log`、`communication_trend_analysis` |
| Niconico | `b_niconico_video_send_log`、`b_m_niconico_video_infomation`、`niconico_info_event`、`niconico_info_filter` |
| ICS | `ics_guild_event_import` |

## 5. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| DB 接続に失敗する | DB 接続環境変数を確認する |
| 起動時に SQL エラーが出る | `db/schema_migrations.py` の対象テーブルと既存 schema を確認する |
| `DB_HOST is set to 'localohst'.` | `DB_HOST` の typo を修正する |
