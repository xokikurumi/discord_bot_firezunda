# ICS 予定イベント取り込み

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-004 |
| 処理名 | ICS 予定イベント取り込み |
| 実装 | `cogs/tasks/ics_guild_event_cog.py`、`services/task/ics_guild_event_service.py` |
| 実行方式 | 定期処理・手動実行 |
| 手動コマンド | `!ics_event_sync`、`/ics_event_sync` |

## 2. 処理概要

ICS ファイルを取得し、未来の VEVENT を Discord scheduled event として作成します。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `ICS_GUILD_EVENT_ENABLED=true` |
| 取得元 | `ICS_GUILD_EVENT_URL` |
| 対象月間隔 | `ICS_GUILD_EVENT_INTERVAL_MONTHS` |
| チェック間隔 | `ICS_GUILD_EVENT_CHECK_INTERVAL_SECONDS` 秒 |
| サーバー別有効化 | `ics_guild_event_config` |

## 4. 定期実行条件

毎月 1 日にチェックし、`(month - 1) % ICS_GUILD_EVENT_INTERVAL_MONTHS == 0` の場合に実行します。
同じ年月の重複実行は `last_run_key` で抑止されます。

## 5. 処理詳細

1. ICS をダウンロードする。
2. VEVENT を解析する。
3. 終了日時が現在より未来のイベントだけを対象にする。
4. ICS 取り込みが有効な Discord サーバーを取得する。
5. 既存 scheduled event と取り込み履歴を確認する。
6. 未作成の event を Discord scheduled event として作成する。
7. `ics_guild_event_import` に取り込み履歴を保存する。
8. `SALES_EVENT` 通知先に作成通知を送信する。

## 6. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | ICS ファイル |
| 参照 | `ics_guild_event_config`、`ics_guild_event_import` |
| 出力 | Discord scheduled event、`ics_guild_event_import`、Discord 通知 |

## 7. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 予定が作成されない | サーバーで ICS 連携が有効か確認する |
| 重複する | `ics_uid` と既存 event 名・開始日の判定を確認する |
| 通知されない | `SALES_EVENT` の通知先設定を確認する |
