# ボイス状態ログ設計

## 概要

Discord ユーザーのボイスチャンネル参加、退出、移動、状態変更を記録する。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `VoiceCog` |
| Service | `VoiceChannelStatusService` |
| Repository | `VoiceChannelStatusRepository` |
| テーブル | `voice_status_log` |

## イベント

| 種別 | 名前 | 内容 |
|---|---|---|
| Event | `on_voice_state_update` | 変更前後のボイス状態を保存する。 |
