# 保守・確認手順

## 1. 定期確認項目

| 項目 | 確認コマンド |
|---|---|
| service 状態 | `sudo systemctl status discord-bot --no-pager` |
| 直近ログ | `sudo journalctl -u discord-bot -n 100 --no-pager` |
| 稼働リリース | `ls -ld /opt/discord/current` |
| Python 依存関係 | `cd /opt/discord/current && sudo -u discord-bot .venv/bin/python -m pip check` |
| 環境変数ファイル | `sudo -u discord-bot test -r /etc/discord-bot/discord-bot.env && echo env-readable` |

## 2. 起動失敗時の確認

service が起動しない場合は、まず journal を確認します。

```bash
sudo journalctl -u discord-bot -n 100 --no-pager
```

Python を手動実行して同じエラーを確認します。

```bash
cd /opt/discord/current
sudo -u discord-bot /opt/discord/current/.venv/bin/python -u /opt/discord/current/main.py
```

## 3. よくある原因

| 症状 | 確認内容 |
|---|---|
| `DISCORD_TOKEN is not set.` | `/etc/discord-bot/discord-bot.env` に `DISCORD_TOKEN` があるか |
| `DB_HOST is set to 'localohst'.` | `DB_HOST` の typo を修正する |
| `status=217/USER` | unit の `User` と `Group` が存在するか |
| DB 接続エラー | `DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_NAME` を確認する |
| import error | `.venv` の依存関係を再インストールする |

## 4. 環境変数変更手順

```bash
sudo vi /etc/discord-bot/discord-bot.env
sudo systemctl restart discord-bot
sudo journalctl -u discord-bot -n 100 --no-pager
```

設定変更後、Discord 上で関連機能を確認します。

## 5. slash command 同期確認

起動時に global sync と、設定により guild sync が実行されます。
反映確認は journal の次のログで行います。

```text
Slash commands synced globally:
Slash commands synced guild=
```

`SLASH_COMMAND_SYNC_TO_GUILDS=false` の場合、guild ごとの即時同期は行われません。

## 6. Niconico Info 確認

```text
/niconico_info_check
/niconico_info_filter list
```

通知先は次で確認します。

```text
/notify_config list
/notify_config category list
```

## 7. Niconico user video 確認

```text
/niconico_user_video_user list
/niconico_user_video_notify list
/niconico_user_video_check
```

## 8. ICS 予定確認

```text
/ics_event_status
/ics_event_sync
```

`/ics_event_sync` は対象サーバーで ICS 連携が有効な場合に実行します。

## 9. P2PQuake 通知確認

P2PQuake は WebSocket 常時接続で通知を受信します。
通知先設定と環境変数を確認します。

```text
/notify_config list
/notify_config category list
```

環境変数の主な確認対象です。

| 変数 | 内容 |
|---|---|
| `P2PQUAKE_ENABLED` | P2PQuake 通知の有効化 |
| `P2PQUAKE_WS_URL` | WebSocket URL |
| `P2PQUAKE_MIN_NOTIFY_SCALE` | 通知する最小震度コード |
| `GSI_TILE_CACHE_DIR` | 地図タイルキャッシュ先 |

## 10. DB バックアップの推奨タイミング

次の作業前には DB バックアップを取得してください。

- リリース前
- 切り戻し前
- DB 関連の不具合調査前
- `schema_migrations.py` に変更が含まれるリリース前

例です。

```bash
mysqldump -h 127.0.0.1 -u discord_bot -p discord_bot > discord_bot_$(date +%Y%m%d%H%M%S).sql
```
