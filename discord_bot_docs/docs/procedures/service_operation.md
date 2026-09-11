# サービス運用手順

## 1. service 状態確認

```bash
sudo systemctl status discord-bot --no-pager
```

開発用 service の場合は次を使用します。

```bash
sudo systemctl status D_discord_dev --no-pager
```

## 2. 起動・停止・再起動

```bash
sudo systemctl start discord-bot
sudo systemctl stop discord-bot
sudo systemctl restart discord-bot
```

OS 起動時に自動起動する場合は enable します。

```bash
sudo systemctl enable discord-bot
```

## 3. ログ確認

直近ログを確認します。

```bash
sudo journalctl -u discord-bot -n 100 --no-pager
```

リアルタイムで追跡します。

```bash
sudo journalctl -u discord-bot -f
```

## 4. 環境変数の確認

環境変数ファイルの読込設定を確認します。

```bash
sudo systemctl cat discord-bot
sudo systemctl show discord-bot -p EnvironmentFiles
```

実行ユーザーが環境変数ファイルを読めることを確認します。

```bash
sudo -u discord-bot test -r /etc/discord-bot/discord-bot.env && echo env-readable
```

## 5. Python 仮想環境の確認

```bash
sudo -u discord-bot test -x /opt/discord/current/.venv/bin/python && echo python-ready
cd /opt/discord/current
sudo -u discord-bot .venv/bin/python -m pip check
```

依存関係を再インストールする場合は次を実行します。

```bash
cd /opt/discord/current
sudo -u discord-bot .venv/bin/python -m pip install -r requirements.txt
sudo -u discord-bot .venv/bin/python -m pip check
sudo systemctl restart discord-bot
```

## 6. DB 接続確認

`.env` の DB 設定に従い、DB へ接続できることを確認します。

```bash
mysql -h 127.0.0.1 -u discord_bot -p discord_bot
```

アプリケーション起動時には `Base.metadata.create_all` による不足テーブル作成と、
`db/schema_migrations.py` の軽量 migration が実行されます。

## 7. Discord コマンド確認

代表的な疎通確認コマンドです。

```text
/roll expression:1d20
/notify_config category list
/ics_event_status
/niconico_info_check
```

管理者権限が必要なコマンドは、管理者権限を持つユーザーで実行します。

## 8. 外部連携の確認

| 機能 | 確認対象 |
|---|---|
| P2PQuake | `P2PQUAKE_ENABLED`、WebSocket 接続ログ、通知チャンネル設定 |
| Ollama 分析 | `OLLAMA_ANALYSIS_ENABLED`、`OLLAMA_URL`、prompt file、few-shot file、Ollama service |
| ICS 予定 | `ICS_GUILD_EVENT_ENABLED`、`ICS_GUILD_EVENT_URL` |
| Niconico Info | `NICONICO_INFO_ENABLED`、`NICONICO_INFO_TARGET_URLS` |
| Niconico user video | `NICONICO_USER_VIDEO_ENABLED`、監視ユーザー設定 |

## 9. 解析 feedback embedding

embedding RAG を有効化する場合は、Ollama 側に embedding model があることを確認します。

```bash
ollama pull nomic-embed-text:latest
```

既存の確認済みフィードバックへ embedding を付与します。

```bash
cd /opt/discord/current
sudo -u discord-bot .venv/bin/python scripts/backfill_message_analysis_feedback_embeddings.py --limit 0
```

embedding model や embedding 対象テキストの仕様を変えた場合は、force 指定で再生成します。

```bash
sudo -u discord-bot .venv/bin/python scripts/backfill_message_analysis_feedback_embeddings.py --limit 0 --force
```

解析挙動を確認済みフィードバックで評価します。

```bash
sudo -u discord-bot .venv/bin/python scripts/evaluate_message_analysis_feedback.py --limit 50
```

## 10. GSI タイルキャッシュ

P2PQuake 通知画像で利用する地理院タイルは、事前キャッシュできます。

```bash
cd /opt/discord/current
sudo -u discord-bot .venv/bin/python deploy/scripts/cache_gsi_tiles.py --dry-run
sudo -u discord-bot .venv/bin/python deploy/scripts/cache_gsi_tiles.py
```

保存先を明示する場合は、`GSI_TILE_CACHE_DIR` と同じ値を指定します。

```bash
sudo -u discord-bot .venv/bin/python deploy/scripts/cache_gsi_tiles.py \
  --cache-dir /opt/discord/current/cache/gsi_tiles \
  --zoom 5 6 7
```
