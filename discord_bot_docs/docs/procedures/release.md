# リリース手順

## 1. リリース方式

このアプリケーションは、タグごとに `/opt/discord/releases/<tag>` へソースを配置し、
`/opt/discord/current` のシンボリックリンクを切り替えてリリースします。

GitLab CI/CD の `deploy_release` job は、Git tag が作成された場合のみ実行されます。
配置後の依存関係更新と service restart は `deploy/scripts/release.sh` で行います。

## 2. 事前確認

リリース前に次を確認します。

```bash
git status --short
python -m compileall -q .
```

GitLab CI/CD を利用する場合は、CI/CD Variables に `DEPLOY_DIR` が設定されていることを確認します。

| 変数 | 値の例 | 備考 |
|---|---|---|
| `DEPLOY_DIR` | `/opt/discord/releases` | 絶対パスで指定 |

Runner は Shell executor を使用します。Docker executor の場合、配置先がコンテナ内ファイルシステムになり、
`deploy_release` job は失敗する設計です。

## 3. タグを作成する

```bash
git tag v1.0.0
git push origin v1.0.0
```

タグ push 後、GitLab CI/CD で `python_compile` と `deploy_release` が成功することを確認します。

## 4. 配置結果を確認する

タグリリース後、サーバーでリリースディレクトリを確認します。

```bash
ls -la /opt/discord/releases/v1.0.0
test -f /opt/discord/releases/v1.0.0/main.py
test -f /opt/discord/releases/v1.0.0/requirements.txt
```

## 5. リリース切り替えを実行する

ソースリポジトリに含まれる `deploy/scripts/release.sh` を root 権限で実行します。

```bash
cd /opt/discord/releases/v1.0.0
sudo ./deploy/scripts/release.sh v1.0.0 discord-bot discord-bot
```

引数は次の通りです。

| 引数 | 省略時 | 内容 |
|---|---|---|
| `<tag>` | 省略不可 | 切り替えるリリースタグ |
| `[service_name]` | `discord-bot` | restart 対象の systemd service 名 |
| `[app_user]` | `discord-bot` | 仮想環境と依存関係更新を実行するユーザー |

開発用 service を切り替える場合の例です。

```bash
cd /opt/discord/releases/v1.0.0
sudo ./deploy/scripts/release.sh v1.0.0 D_discord_dev discord
```

## 6. release.sh が行う処理

`release.sh` は次の処理を実行します。

1. `/opt/discord/releases/<tag>` の存在確認
2. `requirements.txt` と `main.py` の存在確認
3. `/opt/discord/current` を対象リリースへ切り替え
4. リリースディレクトリの所有者を実行ユーザーへ変更
5. `.venv` が無ければ作成
6. `pip install --upgrade pip`
7. `pip install -r requirements.txt`
8. `pip check`
9. systemd service の restart
10. service status の表示

## 7. リリース後確認

```bash
ls -ld /opt/discord/current
sudo systemctl status discord-bot --no-pager
sudo journalctl -u discord-bot -n 100 --no-pager
```

ログで次を確認します。

- `DB initialized.`
- `Cog initialize complete.`
- `Slash commands synced globally:`
- `Bot ready:`

起動時に不足テーブル作成と軽量 schema migration が実行されます。
既存テーブルのカラム追加や一部 unique index の調整も起動時に適用されます。

## 8. Discord 動作確認

管理者権限のある Discord サーバーで代表コマンドを確認します。

```text
/notify_config category list
/roll expression:1d20
/ics_event_status
```

prefix command も併用する場合は、次を確認します。

```text
!roll 1d20
!notify_config category list
```

## 9. リリース完了条件

- GitLab CI/CD の対象タグ pipeline が成功していること。
- `/opt/discord/current` が新タグのディレクトリを指していること。
- systemd service が `active (running)` であること。
- journal に起動エラーが出ていないこと。
- Discord 上で代表コマンドが応答すること。
