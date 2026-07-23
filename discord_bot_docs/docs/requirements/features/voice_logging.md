# ボイス状態ログ要件

## 1. 概要

Discord のボイスチャンネル状態変更を記録し、参加状況や利用状況を後から確認できるようにする。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-VOICE-001 | ユーザーのボイスチャンネル参加を記録できること。 |
| FR-VOICE-002 | ユーザーのボイスチャンネル退出を記録できること。 |
| FR-VOICE-003 | チャンネル移動を変更前後のチャンネル付きで記録できること。 |
| FR-VOICE-004 | ミュート、スピーカーミュート、配信、カメラなどの状態変更を記録できること。 |
| FR-VOICE-005 | 記録にはギルド、ユーザー、変更時刻、変更前後の状態を含めること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | Discord のボイス状態変更イベント |
| 出力 | ボイス状態ログ |

## 4. 関連文書

- [ボイス状態ログ設計](../../basic_design/features/voice_logging.md)
- [ボイス状態ログ詳細](../../detailed_design/features/voice_logging.md)
- [voice_status_log](../../table_definitions/tables/voice_status_log.md)
