# 詳細設計書

## 1. 目的

本書群は、Discord Bot を同等の構成と挙動で再実装できる粒度まで、起動処理、依存生成、Discord Cog、Service、Repository、DB 永続化、外部 API 連携、定期タスク、例外時の扱いを定義する。

本文では実装対象のソース位置は記載せず、機能単位で必要なクラス、メソッド、入力、出力、分岐、永続化仕様を示す。

## 2. 共通詳細

| 文書 | 内容 |
|---|---|
| [起動・DI・Cog 登録詳細](common/startup_and_container.md) | Bot 起動、Intent、Service 生成、Cog 登録、slash command 同期 |
| [DB 初期化・スキーマ移行詳細](common/database_initialization.md) | SQLAlchemy 非同期接続、テーブル作成、軽量マイグレーション |
| [CI/CD 詳細](common/cicd.md) | デプロイ、systemd、リリース切替、運用スクリプト |

## 3. 機能別詳細

| 文書 | 内容 |
|---|---|
| [メッセージログ詳細](features/message_logging.md) | 投稿、編集、削除、履歴取り込み、ユーザー/チャンネルマスタ更新 |
| [ボイス状態ログ詳細](features/voice_logging.md) | ボイス入退室、ミュート、スピーカー、配信状態の保存 |
| [通知設定詳細](features/notification_config.md) | 汎用通知カテゴリ、通知先チャンネル、メンション設定 |
| [リアクション自動化詳細](features/reaction_automation.md) | キーワード登録、NG 抑止、絵文字解析、自動リアクション |
| [ダイスロール詳細](features/dice_roll.md) | `d20` 式評価、手動コマンド、自動ロール判定 |
| [Ollama メッセージ分析詳細](features/ollama_message_analysis.md) | 投稿分析、しきい値判定、リアクション、DM、フィードバック |
| [コミュニケーション傾向分析詳細](features/communication_trend.md) | 半期集計、Ollama レポート生成、集計結果保存 |
| [P2PQuake 通知詳細](features/p2pquake_notification.md) | WebSocket 監視、地震/津波/緊急地震速報通知、画像生成 |
| [Geolonia 住所同期詳細](features/geolonia_address_sync.md) | 住所データ同期、観測点座標補完、キャッシュ更新 |
| [ICS 予定イベント取り込み詳細](features/ics_guild_event.md) | ICS 解析、Discord 予定イベント作成、重複抑止 |
| [Niconico ユーザー投稿通知詳細](features/niconico_user_video.md) | 監視ユーザー、投稿検出、通知先設定、送信済み管理 |
| [Niconico Info 通知詳細](features/niconico_info.md) | HTML 解析、イベント検出、フィルタ、要約通知 |

## 4. 再実装時の前提

- Python の非同期処理を中心に構成し、Discord 連携は `discord.py` の `commands.Bot`、Cog、hybrid command、listener を使用する。
- DB 接続は SQLAlchemy の async engine と `AsyncSession` を使用し、各 Service メソッドは必要な単位で session を生成する。
- 外部 API や HTML 取得などのブロッキング処理は、イベントループを塞がないよう `asyncio.to_thread` で実行する。
- Bot 起動時に DB テーブル作成、軽量マイグレーション、Service 生成、Cog 登録、slash command 同期を順に行う。
- エラーは原則として Bot 全体を停止させず、Discord へのユーザー向けエラー応答または標準出力ログに変換する。
