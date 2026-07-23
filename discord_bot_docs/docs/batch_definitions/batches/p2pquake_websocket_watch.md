# P2PQuake WebSocket 監視

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-002 |
| 処理名 | P2PQuake WebSocket 監視 |
| 実装 | `cogs/disaster/p2pquake_cog.py`、`services/base/p2pquake_service.py` |
| 実行方式 | 常駐監視 |
| 起動契機 | `P2PQuakeCog.cog_load` |

## 2. 処理概要

P2PQuake WebSocket に接続し、地震情報、津波情報、緊急地震速報を受信して Discord へ通知します。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `P2PQUAKE_ENABLED=true` |
| 接続先 | `P2PQUAKE_WS_URL` |
| 再接続間隔 | `P2PQUAKE_RECONNECT_DELAY` 秒 |
| 通知閾値 | `P2PQUAKE_MIN_NOTIFY_SCALE` |

## 4. 処理詳細

1. Bot ready 待ちを行う。
2. JMA 震度観測点同期タスクを起動する。
3. WebSocket 接続を開始する。
4. 対象 code のメッセージを解析する。
5. 重複イベント ID を抑止する。
6. 最大震度が閾値未満の地震系イベントを除外する。
7. `QUAKE` カテゴリの通知先へ本文を送信する。
8. 震源または津波画像が生成可能な場合、画像送信を非同期で起動する。
9. 切断または例外発生時は再接続する。

## 5. 対象イベント

| code | 内容 |
|---:|---|
| 551 | 地震情報 |
| 552 | 津波予報・津波警報 |
| 556 | 緊急地震速報 警報 |

## 6. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | P2PQuake WebSocket メッセージ |
| 参照 | `b_notify_cannel_config`、JMA 観測点、Geolonia 住所データ |
| 出力 | Discord 通知、震源画像、津波画像 |

## 7. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 通知されない | `notify_config` の `QUAKE` 通知先設定を確認する |
| WebSocket 接続エラー | `P2PQUAKE_WS_URL` とネットワークを確認する |
| 地図画像が出ない | `GSI_TILE_CACHE_DIR`、Pillow、フォント、地理データを確認する |
