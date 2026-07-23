# ICS 予定イベント取り込み詳細

## 1. 目的

外部 ICS feed から将来イベントを取得し、guild が明示的に有効化している場合に Discord scheduled event として作成する。作成済み UID と既存 scheduled event の重複を防ぐ。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| IcsGuildEventCog | background task と管理コマンドを提供する |
| IcsGuildEventService | ICS download、parse、guild event 作成、通知を行う |
| IcsEvent | UID、summary、description、location、start/end、url を持つ DTO |
| IcsGuildEventConfigRepository | guild ごとの有効状態を管理する |
| IcsGuildEventImportRepository | 取り込み済み UID を管理する |
| NotifyChannelConfigRepository | `SALES_EVENT` 通知先を取得する |

## 3. コマンド

| コマンド | 権限 | 処理 |
|---|---|---|
| `ics_event_sync` | 管理者 | 現 guild が有効なら手動取り込み |
| `ics_event_enable` | 管理者 | 現 guild の取り込みを有効化 |
| `ics_event_disable` | 管理者 | 現 guild の取り込みを無効化 |
| `ics_event_status` | 管理者 | 有効状態を表示 |

無効 guild で sync した場合は enable を促して終了する。

## 4. 定期実行

機能が無効な場合は終了する。有効な場合は Bot ready 後、`ICS_GUILD_EVENT_CHECK_INTERVAL_SECONDS` ごとに現在日時 JST を確認する。

実行条件は次の通り。

1. day が 1。
2. `(month - 1) % ICS_GUILD_EVENT_INTERVAL_MONTHS == 0`。
3. `YYYY-MM` 形式 run key が直近実行 key と異なる。

## 5. ICS 取得と解析

ICS は URL から 30 秒 timeout で取得し、UTF-8 decode する。改行は CRLF/CR を LF に統一し、行頭が空白または tab の行は前行に連結する。

`BEGIN:VEVENT` から `END:VEVENT` までを event dict とし、`:` で name/value に分割する。
name は `;` より前を大文字 key とする。
value は `\n`、`\N`、`\,`、`\;`、`\\` を unescape する。

## 6. Event 生成

UID、SUMMARY、DTSTART が欠ける event は破棄する。DTEND がない、または DTSTART 以下の場合は開始から 1 日後を終了にする。

日時 parse は次の形式を扱う。

| 形式 | 解釈 |
|---|---|
| `YYYYMMDD` | JST の当日 00:00 |
| `YYYYMMDDTHHMMSSZ` | UTC として parse し JST に変換 |
| `YYYYMMDDTHHMMSS` | JST として parse |

## 7. 取り込み

全 guild 取り込みでは ICS を 1 回だけ download/parse する。
終了日時が現在 JST より未来の event のみを対象にする。
対象 guild は DB で enabled の guild id と Bot が参加中の guild の積集合。

guild 単位では次を満たす event のみ作成する。

1. `ics_guild_event_import(guild_id, ics_uid)` が存在しない。
2. 既存 scheduled event に、正規化済み name と開始日が一致するものがない。

name 正規化は空白を 1 つに畳み、casefold する。

## 8. Discord scheduled event 作成

| 項目 | 値 |
|---|---|
| name | summary の先頭 100 文字 |
| start_time | event.start_time |
| end_time | event.end_time |
| entity_type | external |
| privacy_level | guild_only |
| location | location、url、`TBD` の順で先頭 100 文字 |
| description | description、URL、ICS UID を空行区切りで結合し先頭 1000 文字 |
| reason | `ICS scheduled event import` |

作成後、guild id、ICS UID、source URL、scheduled event id、summary、start_time を insert ignore で保存する。

## 9. 通知

作成成功後、`SALES_EVENT` カテゴリの有効通知設定へ送信する。
本文はイベント名、開始/終了日時、場所、URL、Discord event URL を含める。
通知先 channel が Bot cache にない場合は warning ログを出して続行する。
