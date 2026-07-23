# Geolonia 住所同期要件

## 1. 概要

地震関連通知で地点名から座標を解決するため、Bot 起動後に Geolonia の住所データを同期し、住所検索に利用できる状態へ更新する。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-GEO-001 | Bot 起動後に Geolonia 住所同期タスクを開始できること。 |
| FR-GEO-002 | 設定により同期処理を有効化・無効化できること。 |
| FR-GEO-003 | 同期履歴が存在しない場合は住所データを登録できること。 |
| FR-GEO-004 | 最終同期日時が最新予定同期日より古い場合は住所データを更新できること。 |
| FR-GEO-005 | 最終同期日時が最新予定同期日以降の場合は同期をスキップできること。 |
| FR-GEO-006 | 取得した都道府県、市区町村、地域、緯度、経度を保存できること。 |
| FR-GEO-007 | 同期完了時に同期履歴を更新できること。 |
| FR-GEO-008 | 同期後に住所解決用キャッシュをクリアし、更新後データを参照できること。 |

## 3. 予定同期日

| ID | 要件 |
|---|---|
| FR-GEO-SCHEDULE-001 | 毎年 1 月 1 日を予定同期日として扱うこと。 |
| FR-GEO-SCHEDULE-002 | 毎年 6 月 1 日を予定同期日として扱うこと。 |
| FR-GEO-SCHEDULE-003 | 現在日時から見た最新の予定同期日を基準に同期要否を判定すること。 |

## 4. 非機能要求

| ID | 要件 |
|---|---|
| NFR-GEO-001 | 住所データ取得に失敗しても Bot 全体を停止しないこと。 |
| NFR-GEO-002 | 同期処理はバックグラウンドで実行し、P2PQuake 監視を妨げないこと。 |
| NFR-GEO-003 | 住所データの登録は、途中失敗時に同期完了として扱わないこと。 |

## 5. 関連文書

- [Geolonia 住所同期設計](../../basic_design/features/geolonia_address_sync.md)
- [Geolonia 住所同期詳細](../../detailed_design/features/geolonia_address_sync.md)
- [Geolonia 住所同期バッチ](../../batch_definitions/batches/geolonia_address_sync.md)
- [b_geolonia_address](../../table_definitions/tables/b_geolonia_address.md)
- [b_geolonia_sync_state](../../table_definitions/tables/b_geolonia_sync_state.md)
