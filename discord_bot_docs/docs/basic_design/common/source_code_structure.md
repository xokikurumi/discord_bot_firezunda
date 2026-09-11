# 現行ソースコード構成

## 1. 目的

`D:\6000.PROJECTS\discord_bot_firezunda\discord_bot_src` の現行ローカルソースを読む際の入口として、
ディレクトリ構成、主要な責務、データと設定の流れ、保守時の注意点を整理する。

本書はソースコードから読み取れる構造を記録するものであり、詳細な処理仕様は
[詳細設計書](../../detailed_design/README.md) と各機能別文書を参照する。

## 2. 構成方針

Bot は `discord.py` の Cog を外部インターフェース層、Service をユースケース層、
Repository と SQLAlchemy model を永続化層として扱う構成になっている。
この分離により、Discord のイベントやコマンド処理を薄く保ち、DB 操作や外部 API 連携を
Service / Repository 側へ寄せている。

起動時に `main.py` が DB 初期化、Service 生成、Cog 登録、slash command 同期を行う。
Service 生成用の `Container` は `main.py` 内に置かれており、独立した DI フレームワークは使わない。
機能数が増えても起動時の依存関係を追いやすくするための、軽量な手動 DI と見なせる。

## 3. ディレクトリ構成

| パス | 役割 |
|---|---|
| `main.py` | Bot 起動、DB 初期化、Service 生成、Cog 登録、slash command 同期 |
| `config.py` | 環境変数の読み取り、既定値、Ollama prompt 既定値 |
| `constants.py` | 通知カテゴリなど、複数機能で共有する定数 |
| `cogs/` | Discord command、listener、background task の入口 |
| `services/` | 機能ごとのユースケース、外部 API 取得、通知本文生成 |
| `repositories/` | SQLAlchemy session を使った DB 操作 |
| `models/` | SQLAlchemy ORM model |
| `db/` | async engine / session と起動時スキーマ補正 |
| `deploy/` | systemd、デプロイスクリプト、運用補助 |
| `config/` | Ollama 分析 prompt や few-shot 例などの実行時設定 |

## 4. 主要機能の配置

| 機能 | Cog | Service | 主な永続化 |
|---|---|---|---|
| メッセージログ | `MessageCog` | `MessageLogService` | `message_log`、`message_edit_log`、`message_delete_log` |
| ボイスログ | `VoiceCog` | `VoiceChannelStatusService` | `voice_status_log` |
| リアクション自動化 | `MessageReactionCog` | `MessageReactionService` | `b_reaction_keywords` |
| ダイスロール | `DiceRollCog` | `DiceRollService` | なし |
| リアクション抽選 | `ReactionLotteryCog` | `ReactionLotteryService` | なし |
| P2PQuake 通知 | `P2PQuakeCog` | `P2PQuakeService` | `b_notify_cannel_config`、震度/住所マスタ |
| ICS 予定イベント | `IcsGuildEventCog` | `IcsGuildEventService` | `ics_guild_event_config`、`ics_guild_event_import` |
| Niconico 投稿通知 | `NiconicoUserVideoCog` | `NiconicoUserVideoService` | Niconico 投稿通知関連テーブル |
| Niconico Info 通知 | `NiconicoInfoCog` | `NiconicoInfoService` | `niconico_info_event`、`niconico_info_filter` |
| Ollama 分析 | `MessageWatcherCog`、`AnalysisCog` | `MessageWatcherService` | 分析ログ、フィードバック、ホワイトリスト |
| コミュニケーション傾向分析 | `CommunicationTrendCog` | `CommunicationTrendService` | `communication_trend_analysis` |

## 5. データと設定の流れ

1. `config.py` が環境変数を読み取り、DB、Discord、外部 API、Ollama 関連の設定値を作る。
2. `db/session.py` が SQLAlchemy async engine と session factory を作る。
3. `main.py` の `init_db` が `Base.metadata.create_all` と軽量マイグレーションを実行する。
4. `Container` が session factory と Bot 参照を Service へ渡す。
5. Cog は command / listener / task の入口として Service を呼び出す。
6. Service は Repository を通じて DB を更新し、必要に応じて Discord や外部 API へアクセスする。

## 6. 設計上の前提

- Discord 連携は `commands.Bot`、Cog、hybrid command、listener を中心にする。
- DB は MySQL 系 URL を既定とし、SQLAlchemy async と `aiomysql` を使用する。
- 起動時マイグレーションは既存テーブルを破壊せず、不足列・不足 index の追加に限定する。
- ユーザー操作を伴う管理系コマンドは原則として guild 限定、更新系は管理者権限を要求する。
- 外部 API 取得や分析処理は失敗しても Bot 全体を停止させず、ログまたはユーザー向け応答に変換する。

## 7. 今後変更するときの注意点

- Cog を追加した場合は `main.py` の import、Service 生成、`setup_cogs` の登録順を更新する。
- 永続化を追加した場合は model、repository、テーブル定義書、起動時マイグレーションの整合を確認する。
- 通知カテゴリを追加・削除した場合は `constants.py`、通知設定設計、コマンド一覧を同時に更新する。
- slash command は Discord 側の同期状態に依存するため、実装直後に反映されない可能性を考慮する。
- 既存テーブルの列変更は `create_all` では反映されないため、必要に応じて idempotent な補正を追加する。

## 8. 要確認

- 対象 src リポジトリのローカル `main` は確認時点で `origin/main` より 16 commits 遅れている。
  本書はユーザー指定のローカルソースを基準にしている。
- `jma_weather_xml` 系の詳細設計・テーブル定義は docs 側に過去文書として残っているが、
  現行ローカルソースには Cog、Service、Repository、Model、設定値が存在しない。
