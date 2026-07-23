# 基本設計書

## 1. 目的

要件定義に記載した機能を、利用者視点の機能構成、処理方針、データ利用方針へ展開する。
本書は詳細設計の前段として、機能単位の責務と連携関係を整理する。

## 2. 共通設計

| 文書 | 内容 |
|---|---|
| [システム構成](common/system_architecture.md) | Bot 全体の構成と機能配置 |
| [起動・初期化設計](common/startup.md) | 起動時初期化と Cog 登録方針 |
| [データ設計方針](common/data_design.md) | DB、ログ、設定、外部基礎データの扱い |
| [外部連携設計](common/external_integrations.md) | Discord、外部 API、地図、AI 連携 |
| [エラー処理設計](common/error_handling.md) | 例外、通知失敗、外部連携失敗時の方針 |
| [セキュリティ設計](common/security.md) | 秘密情報、権限、運用上の注意 |
| [運用設計](common/operations.md) | CI/CD、リリース、保守、障害対応 |

## 3. 機能別設計

| 文書 | 内容 |
|---|---|
| [メッセージログ設計](features/message_logging.md) | 投稿・編集・削除ログ |
| [ボイス状態ログ設計](features/voice_logging.md) | ボイスチャンネル状態変更ログ |
| [通知設定設計](features/notification_config.md) | 通知先、メンション、カテゴリ管理 |
| [リアクション自動化設計](features/reaction_automation.md) | キーワード一致によるリアクション付与 |
| [ダイスロール設計](features/dice_roll.md) | ダイス式評価 |
| [Ollama メッセージ分析設計](features/ollama_message_analysis.md) | メッセージ内容分析 |
| [コミュニケーション傾向分析設計](features/communication_trend.md) | 半期単位の傾向分析 |
| [P2PQuake 通知設計](features/p2pquake_notification.md) | 地震・津波・緊急地震速報通知 |
| [Geolonia 住所同期設計](features/geolonia_address_sync.md) | 住所データ同期と住所解決補助 |
| [ICS 予定イベント取り込み設計](features/ics_guild_event.md) | ICS 予定の Discord イベント化 |
| [Niconico ユーザー投稿通知設計](features/niconico_user_video.md) | ユーザー投稿動画の検出・通知 |
| [Niconico Info 通知設計](features/niconico_info.md) | Niconico 記事検出・通知 |

## 4. 関連文書

- [要件定義書](../requirements/README.md)
- [詳細設計書](../detailed_design/README.md)
- [テーブル定義書](../table_definitions/README.md)
