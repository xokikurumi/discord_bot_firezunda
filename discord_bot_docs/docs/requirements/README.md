# 要件定義書

## 1. 目的

Discord サーバー上で利用する Bot として、メッセージ記録、通知、外部情報連携、定期処理、管理用コマンドを提供する。
本書では、機能要求と非機能要求を分割し、基本設計・詳細設計・テーブル定義・手順書へ展開しやすい単位で整理する。

## 2. 文書構成

| 区分 | 文書 | 内容 |
|---|---|---|
| 共通要件 | [システム共通要件](common/system.md) | 利用者、前提条件、共通動作 |
| 共通要件 | [非機能要件](common/non_functional.md) | セキュリティ、可用性、性能、保守性 |
| 共通要件 | [データ要件](common/data.md) | 保存対象、データ分類、保持方針 |
| 共通要件 | [運用要件](common/operations.md) | CI/CD、リリース、監視、復旧 |
| 共通要件 | [制約・前提条件](common/constraints.md) | 外部制約、環境制約、未対応事項 |
| 機能要件 | [メッセージログ](features/message_logging.md) | 投稿・編集・削除ログ、バックフィル |
| 機能要件 | [ボイス状態ログ](features/voice_logging.md) | ボイスチャンネル参加・退出・移動ログ |
| 機能要件 | [リアクション自動化](features/reaction_automation.md) | キーワード反応、NG 条件、管理コマンド |
| 機能要件 | [ダイスロール](features/dice_roll.md) | ダイス式評価、手動・自動ロール |
| 機能要件 | [リアクション抽選](features/reaction_lottery.md) | リアクション応募、当選者抽選、早期終了 |
| 機能要件 | [通知設定](features/notification_config.md) | 通知カテゴリ別の送信先管理 |
| 機能要件 | [P2PQuake 通知](features/p2pquake_notification.md) | 地震・津波・緊急地震速報通知 |
| 機能要件 | [Geolonia 住所同期](features/geolonia_address_sync.md) | 住所データ同期、同期履歴管理 |
| 機能要件 | [ICS 予定イベント取り込み](features/ics_guild_event.md) | ICS 予定の Discord イベント化 |
| 機能要件 | [Niconico ユーザー投稿通知](features/niconico_user_video.md) | ユーザー別投稿検出・通知 |
| 機能要件 | [Niconico Info 通知](features/niconico_info.md) | 記事検出、フィルタ、通知 |
| 機能要件 | [Ollama メッセージ分析](features/ollama_message_analysis.md) | メッセージ分析、しきい値通知 |
| 機能要件 | [コミュニケーション傾向分析](features/communication_trend.md) | 半期単位の投稿傾向集計 |
| 機能要件 | [コマンド提供](features/command_interface.md) | prefix command と slash command |

## 3. 要件 ID 体系

| 接頭辞 | 区分 |
|---|---|
| FR-SYS | システム共通 |
| FR-LOG | メッセージログ |
| FR-VOICE | ボイス状態ログ |
| FR-REACTION | リアクション自動化 |
| FR-DICE | ダイスロール |
| FR-LOTTERY | リアクション抽選 |
| FR-NOTIFY | 通知設定 |
| FR-QUAKE | P2PQuake 通知 |
| FR-GEO | Geolonia 住所同期 |
| FR-ICS | ICS 予定イベント取り込み |
| FR-NICO-USER | Niconico ユーザー投稿通知 |
| FR-NICO-INFO | Niconico Info 通知 |
| FR-AI | Ollama メッセージ分析 |
| FR-TREND | コミュニケーション傾向分析 |
| FR-CMD | コマンド提供 |
| NFR | 非機能 |
| DATA | データ |
| OPS | 運用 |
| CON | 制約 |

## 4. 関連文書

- [基本設計書](../basic_design/README.md)
- [詳細設計書](../detailed_design/README.md)
- [バッチ処理定義一覧](../batch_definitions/README.md)
- [テーブル定義書](../table_definitions/README.md)
