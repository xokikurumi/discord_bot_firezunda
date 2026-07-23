# P2PQuake 通知要件

## 1. 概要

P2PQuake から受信した地震、津波、緊急地震速報関連イベントを整形し、Discord の通知先へ投稿する。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-QUAKE-001 | P2PQuake WebSocket から対象イベントを受信できること。 |
| FR-QUAKE-002 | 地震情報、津波情報、緊急地震速報を通知対象として扱えること。 |
| FR-QUAKE-003 | 受信イベントを Discord 投稿用に整形できること。 |
| FR-QUAKE-004 | 通知設定に従って対象チャンネルへ投稿できること。 |
| FR-QUAKE-005 | 観測点や住所データを利用して、地点情報を補完できること。 |
| FR-QUAKE-006 | 短時間の重複イベントを抑止できること。 |
| FR-QUAKE-007 | 地図や震度情報を視覚的に確認できる画像を生成できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | P2PQuake イベント、通知設定、観測点データ、住所データ |
| 出力 | Discord 通知メッセージ、通知画像 |

## 4. 関連文書

- [P2PQuake 通知設計](../../basic_design/features/p2pquake_notification.md)
- [P2PQuake 通知詳細](../../detailed_design/features/p2pquake_notification.md)
- [P2PQuake WebSocket 監視](../../batch_definitions/batches/p2pquake_websocket_watch.md)
