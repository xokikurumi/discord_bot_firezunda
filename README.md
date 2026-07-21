# discord_bot_firezunda

Discord サーバーの運用を補助する多機能 Bot です。メッセージやボイスチャンネルのログ記録、リアクション自動化、ダイスロール、地震情報通知、Discord 予定イベントの同期、ニコニコ関連通知、Ollama を利用したメッセージ分析を扱います。

## 主な機能

- メッセージ作成、編集、削除ログの保存
- ボイスチャンネル入退室ログの保存
- キーワードに応じたリアクション自動付与
- `discord.py` のハイブリッドコマンドによる prefix コマンドと slash コマンド対応
- ダイス式のロール
- P2PQuake を利用した地震情報通知
- ICS カレンダーの Discord 予定イベント同期
- ニコニコ動画ユーザー投稿通知
- ニコニコインフォ記事通知とキーワードフィルタ
- Ollama によるメッセージ分析と半期ごとのコミュニケーション傾向分析
- MySQL への永続化と起動時のテーブル初期化

## 必要環境

- Python 3.10 以上
- MySQL
- Discord Bot Token
- 任意: Ollama

## セットアップ

```bash
cd discord_bot_src
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS の場合は、仮想環境の有効化コマンドを次のように読み替えてください。

```bash
source .venv/bin/activate
```

## 環境変数

最低限、次の環境変数を設定してください。

| 変数 | 内容 |
|---|---|
| `DISCORD_TOKEN` | Discord Bot Token |
| `DB_USER` | MySQL ユーザー名 |
| `DB_PASSWORD` | MySQL パスワード |
| `DB_HOST` | MySQL ホスト |
| `DB_PORT` | MySQL ポート |
| `DB_NAME` | MySQL データベース名 |

代表的な任意設定は次の通りです。

| 変数 | 内容 |
|---|---|
| `SLASH_COMMAND_SYNC_TO_GUILDS` | 起動時に参加サーバーへ slash コマンドを同期するか |
| `OLLAMA_ANALYSIS_ENABLED` | Ollama によるメッセージ分析を有効化するか |
| `OLLAMA_URL` | Ollama Chat API の URL |
| `OLLAMA_MODEL` | 分析に使用する Ollama モデル |
| `P2PQUAKE_ENABLED` | 地震情報通知を有効化するか |
| `P2PQUAKE_MIN_NOTIFY_SCALE` | 通知対象にする最小震度コード |
| `ICS_GUILD_EVENT_ENABLED` | ICS 予定イベント同期を有効化するか |
| `ICS_GUILD_EVENT_URL` | 同期対象の ICS URL |
| `NICONICO_USER_VIDEO_ENABLED` | ニコニコ動画ユーザー投稿通知を有効化するか |
| `NICONICO_INFO_ENABLED` | ニコニコインフォ通知を有効化するか |
| `NICONICO_INFO_TARGET_URLS` | 監視対象カテゴリ URL のカンマ区切りリスト |

トークン、パスワード、接続情報はリポジトリへコミットしないでください。

## 起動

```bash
cd discord_bot_src
python main.py
```

起動時にデータベースの初期化、軽量なスキーマ移行、Cog の登録、slash コマンド同期が実行されます。

## 主要コマンド

多くのコマンドは `!` prefix と slash コマンドの両方に対応しています。

| 用途 | コマンド例 |
|---|---|
| ダイスロール | `!roll 1d20+5` / `/roll` |
| メッセージログのバックフィル | `!backfill_message_logs 1000` / `/backfill_message_logs` |
| リアクション設定 | `!reaction add <keyword> <reaction>` / `/reaction add` |
| 通知先設定 | `!notify_config add #channel none QUAKE` / `/notify_config add` |
| ICS 同期 | `!ics_event_sync` / `/ics_event_sync` |
| ニコニコユーザー投稿確認 | `!niconico_user_video_check` / `/niconico_user_video_check` |
| ニコニコインフォ確認 | `!niconico_info_check` / `/niconico_info_check` |
| コミュニケーション傾向分析 | `!communication_trend_analyze` / `/communication_trend_analyze` |

管理系コマンドの多くは Discord の管理者権限を必要とします。

## ドキュメント

詳細な設計情報は `discord_bot_docs` にまとめています。

- 要件定義
- 基本設計
- 詳細設計
- テーブル定義

MkDocs で確認する場合は次のコマンドを利用できます。

```bash
cd discord_bot_docs
pip install -r requirements.txt
mkdocs serve
```

## 運用

systemd 用の設定例とリリース補助スクリプトを用意しています。サーバー上で常駐運用する場合は、環境変数ファイルを作成し、実行ユーザー、配置先、ログ確認方法を運用環境に合わせて調整してください。

## 開発メモ

- Bot には Message Content Intent などの Discord 側設定が必要です。
- slash コマンドはグローバル同期の場合、反映まで時間がかかることがあります。
- P2PQuake の画像通知で日本語が文字化けする場合は、日本語対応フォントのパスを設定してください。
- 外部サービスのページ構造や API 仕様が変わった場合、通知取得処理の調整が必要になることがあります。

## ライセンス

本プロジェクトの利用にあたっては、使用している各ライブラリのライセンスに従ってください。

個人利用、検証、学習目的での利用は問題ありません。公開、再配布、商用利用などを行う場合は、依存ライブラリのライセンス条件を確認したうえで利用してください。
