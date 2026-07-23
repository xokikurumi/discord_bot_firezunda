# DB テーブル定義生成

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-011 |
| 処理名 | DB テーブル定義生成 |
| 実装 | `utils/generate_db_table_definitions.py` |
| 実行方式 | 手動スクリプト |
| 起動契機 | 開発・保守時 |

## 2. 処理概要

現在接続可能な MySQL の `INFORMATION_SCHEMA` からテーブル、カラム、index、外部キー情報を取得し、Markdown のテーブル定義書を生成します。

## 3. 実行例

```bash
python utils/generate_db_table_definitions.py
```

## 4. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | `INFORMATION_SCHEMA.TABLES`、`COLUMNS`、`STATISTICS`、`KEY_COLUMN_USAGE` |
| 出力 | `DB_TABLE_DEFINITIONS.md` |

## 5. 注意事項

DB 接続先は `config.py` の環境変数設定に依存します。
本番 DB に接続して実行する場合は、参照権限と出力先を確認してください。
