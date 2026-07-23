# 通知設定要件

## 1. 概要

通知カテゴリごとに送信先チャンネル、メンション、有効状態を管理し、各通知機能から共通利用できるようにする。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-NOTIFY-001 | 管理者は通知カテゴリごとに送信先チャンネルを登録できること。 |
| FR-NOTIFY-002 | 管理者は通知カテゴリごとにメンション文字列を設定できること。 |
| FR-NOTIFY-003 | 管理者は通知設定を有効化・無効化できること。 |
| FR-NOTIFY-004 | 利用者は通知カテゴリ一覧を確認できること。 |
| FR-NOTIFY-005 | 利用者は現在の通知設定一覧を確認できること。 |
| FR-NOTIFY-006 | 通知カテゴリは地震、予定イベント、Niconico Info、Niconico ユーザー投稿を扱えること。 |

## 3. 権限

| 操作 | 権限 |
|---|---|
| 追加・有効化・無効化 | 管理者 |
| カテゴリ確認・一覧確認 | サーバー内利用者 |

## 4. 関連文書

- [通知設定設計](../../basic_design/features/notification_config.md)
- [通知設定詳細](../../detailed_design/features/notification_config.md)
- [b_notify_cannel_config](../../table_definitions/tables/b_notify_cannel_config.md)
