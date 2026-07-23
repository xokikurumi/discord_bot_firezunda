# Niconico ユーザー投稿動画確認・通知

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-007 |
| 処理名 | Niconico ユーザー投稿動画確認・通知 |
| 実装 | `cogs/tasks/niconico_user_video_cog.py`、`services/task/niconico_user_video_service.py` |
| 実行方式 | 定期処理・手動実行 |
| 手動コマンド | `!niconico_user_video_check`、`/niconico_user_video_check` |

## 2. 処理概要

監視対象の Niconico ユーザーについて、通常動画とショート動画の最新投稿を確認し、未通知の動画を Discord へ通知します。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `NICONICO_USER_VIDEO_ENABLED=true` |
| 実行周期 | 15 分ごとの時刻境界 |
| 実行タイミング | `n:00`、`n:15`、`n:30`、`n:45` |
| 監視対象 | `b_m_niconico_video_infomation` |
| 通知先 | `b_niconico_notify_cannel_config` |

## 4. 処理詳細

1. 次の 15 分境界まで待機する。
2. 有効な監視対象ユーザー ID を取得する。
3. Niconico nvapi から通常動画の最新投稿を取得する。
4. Niconico shorts ページからショート動画候補を取得する。
5. 未登録リンクを `b_niconico_video_send_log` に保存する。
6. 未送信 row を取得する。
7. ユーザー別通知先へ Discord 通知する。
8. 通知できた row を送信済みに更新する。

## 5. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | Niconico nvapi、Niconico shorts HTML |
| 参照 | `b_m_niconico_video_infomation`、`b_niconico_notify_cannel_config` |
| 出力 | `b_niconico_video_send_log`、Discord 通知 |

## 6. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 検出されない | 監視対象ユーザー ID、Niconico API 応答を確認する |
| 通知されない | ユーザー別通知先設定を確認する |
| 重複通知される | `b_niconico_video_send_log.link` の登録状態を確認する |
