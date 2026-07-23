# JMA 震度観測点同期

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-003 |
| 処理名 | JMA 震度観測点同期 |
| 実装 | `services/base/p2pquake_service.py` |
| 実行方式 | 定期処理 |
| 起動契機 | P2PQuake WebSocket 監視起動時 |

## 2. 処理概要

気象庁の震度観測点ページを取得し、観測点名、住所、緯度、経度を DB に同期します。
P2PQuake の震度地点を地図上に描画するために使用します。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `JMA_SHINDO_STATION_SYNC_ENABLED=true` |
| 同期間隔日数 | `JMA_SHINDO_STATION_SYNC_INTERVAL_DAYS` |
| チェック間隔 | `JMA_SHINDO_STATION_SYNC_CHECK_INTERVAL_SECONDS` 秒 |
| 取得元 | `JMA_SHINDO_STATION_URL` |

## 4. 処理詳細

1. 最終同期日時を `b_jma_sync_state` から取得する。
2. 未同期または同期間隔を超過している場合のみ処理する。
3. 気象庁ページを取得する。
4. HTML table から震度観測点情報を抽出する。
5. 度分形式の座標を十進緯度経度へ変換する。
6. `b_jma_shindo_station` に upsert する。
7. 同期状態を更新する。

## 5. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | 気象庁 震度観測点 HTML |
| 出力 | `b_jma_shindo_station`、`b_jma_sync_state` |

## 6. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 同期失敗 | 取得元 URL と HTML 構造変更を確認する |
| 地点が地図に出ない | `b_jma_shindo_station` の座標データを確認する |
