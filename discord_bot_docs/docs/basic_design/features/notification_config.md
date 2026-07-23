# 通知設定設計

## 概要

通知カテゴリごとの送信先チャンネル、メンション、状態をギルド単位で管理する。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `P2PQuakeCog` |
| Service | `P2PQuakeService` |
| Repository | `NotifyChannelConfigRepository` |
| テーブル | `b_notify_cannel_config` |

## コマンド

| コマンド | 内容 |
|---|---|
| `notify_config add` | 通知先を追加する。 |
| `notify_config list` | 通知設定一覧を表示する。 |
| `notify_config category list` | 通知カテゴリ一覧を表示する。 |
| `notify_config enable` | 通知設定を有効化する。 |
| `notify_config disable` | 通知設定を無効化する。 |

## 通知カテゴリ

| カテゴリ | 用途 |
|---|---|
| `QUAKE` | P2PQuake / 地震通知 |
| `SALES_EVENT` | ICS 予定イベント通知 |
| `NICONICO_INFO` | Niconico Info 通知 |
| `NICONICO_USER_VIDEO` | Niconico ユーザー投稿通知 |
