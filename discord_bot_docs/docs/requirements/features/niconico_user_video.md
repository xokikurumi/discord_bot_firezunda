# Niconico ユーザー投稿通知要件

## 1. 概要

監視対象の Niconico ユーザーについて新規投稿動画を検出し、未通知の動画を Discord へ通知する。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-NICO-USER-001 | 管理者は監視対象ユーザーを追加できること。 |
| FR-NICO-USER-002 | 管理者は監視対象ユーザーの一覧を確認できること。 |
| FR-NICO-USER-003 | 管理者は監視対象ユーザーを無効化できること。 |
| FR-NICO-USER-004 | ユーザーごとの通知先チャンネルとメンションを管理できること。 |
| FR-NICO-USER-005 | 通常動画とショート動画の新規投稿を検出できること。 |
| FR-NICO-USER-006 | 未通知動画を通知し、通知済み状態を保存できること。 |
| FR-NICO-USER-007 | 定期確認を 15 分単位で実行できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | 監視対象ユーザー、Niconico 投稿情報、通知設定 |
| 出力 | 動画情報、送信ログ、Discord 通知 |

## 4. 関連文書

- [Niconico ユーザー投稿通知設計](../../basic_design/features/niconico_user_video.md)
- [Niconico ユーザー投稿通知詳細](../../detailed_design/features/niconico_user_video.md)
- [Niconico ユーザー投稿動画確認・通知](../../batch_definitions/batches/niconico_user_video_check.md)
- [b_m_niconico_video_infomation](../../table_definitions/tables/b_m_niconico_video_infomation.md)
- [b_niconico_video_send_log](../../table_definitions/tables/b_niconico_video_send_log.md)
