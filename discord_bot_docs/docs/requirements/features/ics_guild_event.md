# ICS 予定イベント取り込み要件

## 1. 概要

ICS 形式の予定を取得し、Discord の予定イベントとして登録し、登録結果を通知できるようにする。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-ICS-001 | 管理者はギルド単位で ICS 取り込み設定を有効化・無効化できること。 |
| FR-ICS-002 | ICS URL から予定を取得できること。 |
| FR-ICS-003 | 取得した予定を Discord の予定イベントとして作成できること。 |
| FR-ICS-004 | 取り込み済み ICS UID を記録し、重複作成を防止できること。 |
| FR-ICS-005 | 管理者は手動同期を実行できること。 |
| FR-ICS-006 | 作成した予定イベントを通知設定に従って通知できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | ICS URL、ギルド設定、通知設定 |
| 出力 | Discord 予定イベント、取り込み履歴、通知メッセージ |

## 4. 関連文書

- [ICS 予定イベント取り込み設計](../../basic_design/features/ics_guild_event.md)
- [ICS 予定イベント取り込み詳細](../../detailed_design/features/ics_guild_event.md)
- [ICS 予定イベント取り込みバッチ](../../batch_definitions/batches/ics_guild_event_import.md)
- [ics_guild_event_config](../../table_definitions/tables/ics_guild_event_config.md)
- [ics_guild_event_import](../../table_definitions/tables/ics_guild_event_import.md)
