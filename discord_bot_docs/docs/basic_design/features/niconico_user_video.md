# Niconico ユーザー投稿通知設計

## 概要

監視対象の Niconico ユーザーについて、通常動画とショート動画の最新投稿を検出し通知する。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `NiconicoUserVideoCog` |
| Service | `NiconicoUserVideoService` |
| Repository | `NiconicoUserVideoInfoRepository`, `NiconicoNotifyChannelConfigRepository`, `NiconicoVideoSendLogRepository` |
| テーブル | `b_m_niconico_video_infomation`, `b_niconico_notify_cannel_config`, `b_niconico_video_send_log` |

## コマンド

| コマンド | 内容 |
|---|---|
| `niconico_user_video_check` | 手動で投稿確認を行う。 |
| `niconico_user_video_user add/list/remove` | 監視対象ユーザーを管理する。 |
| `niconico_user_video_notify add/list/enable/disable` | ユーザー別通知先を管理する。 |

## 定期処理

| 項目 | 内容 |
|---|---|
| 実行間隔 | 15 分単位で確認する。 |
| 重複防止 | 動画 ID と送信済み状態で通知済み動画を管理する。 |
