# jma_weather_xml_event

!!! warning "現行ソース未確認"
    `D:\6000.PROJECTS\discord_bot_firezunda\discord_bot_src` の現行ローカルソースには、
    この SQLAlchemy model と起動時マイグレーションが存在しない。
    この文書は過去実装または検討内容として残しているため、現行DB定義として扱わない。

## 概要

- テーブル名: `jma_weather_xml_event`
- 分類: タスク・通知
- 説明: 気象庁防災気象情報 XML の検出イベントと通知済み状態を保存します。

## カラム定義

| No | カラム名 | 型 | NULL | デフォルト | キー | 説明 |
|---:|---|---|---|---|---|---|
| 1 | `id` | `INTEGER` | 不可 |  | PK | 内部管理ID。 |
| 2 | `source_key` | `VARCHAR(255)` | 不可 |  | UK/IDX | Atom entry から作成する重複判定キー。 |
| 3 | `title` | `TEXT` | 不可 |  |  | Atom entry の title。 |
| 4 | `report_title` | `TEXT` | 可 |  |  | XML 詳細の Title。未取得時は title。 |
| 5 | `info_type` | `VARCHAR(100)` | 可 |  |  | XML 詳細の InfoType。 |
| 6 | `author` | `TEXT` | 可 |  |  | Atom entry の author name。 |
| 7 | `headline` | `TEXT` | 可 |  |  | XML 詳細の Text。未取得時は Atom content。 |
| 8 | `content` | `TEXT` | 可 |  |  | Atom entry の content。 |
| 9 | `area_text` | `TEXT` | 可 |  |  | 対象地域名のカンマ区切り。 |
| 10 | `kind_text` | `TEXT` | 可 |  |  | 警報・注意報名と状態のカンマ区切り。 |
| 11 | `link` | `TEXT` | 可 |  |  | XML 詳細 URL。 |
| 12 | `updated_at` | `DATETIME` | 可 |  |  | Atom entry の updated。 |
| 13 | `send_flg` | `BOOLEAN` | 不可 | False | IDX | Discord 通知済み、または通知対象外なら true。 |
| 14 | `delete_flg` | `BOOLEAN` | 不可 | False | IDX | 論理削除済みなら true。 |
| 15 | `created_at` | `DATETIME` | 不可 | now() |  | 作成日時。 |

## 制約

| 制約名 | 種別 | カラム | 詳細 |
|---|---|---|---|
| `(unnamed)` | `PrimaryKeyConstraint` | `id` |  |
| `uq_jma_weather_xml_event_source_key` | `UniqueConstraint` | `source_key` | 同一イベントの重複保存を防止する。 |

## インデックス

| インデックス名 | ユニーク | カラム |
|---|---|---|
| `ix_jma_weather_xml_event_delete_flg` | いいえ | `delete_flg` |
| `ix_jma_weather_xml_event_send_flg` | いいえ | `send_flg` |
| `ix_jma_weather_xml_event_source_key` | はい | `source_key` |

## 備考

- `send_flg=false` かつ `delete_flg=false` の行が未送信通知対象です。
- 起動直後通知抑止や注意報除外により通知しない行も、再通知防止のため `send_flg=true` で保存されます。
