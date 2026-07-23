# 初期セットアップ手順

## 1. 前提パッケージを確認する

サーバーで Python、venv、MySQL または MariaDB、systemd が利用できることを確認します。

```bash
python3 --version
systemctl --version
mysql --version
```

Python は 3.10 以上を使用します。

## 2. 実行ユーザーを作成する

本番用の systemd unit は `discord-bot` ユーザーで実行します。

```bash
sudo useradd --system --home-dir /opt/discord --shell /sbin/nologin discord-bot
```

開発用 unit `D_discord_dev.service` を使う場合は、unit に定義されている `discord` ユーザーを用意します。

```bash
id discord
```

存在しない場合は、運用方針に合わせて作成してください。

## 3. ディレクトリを作成する

```bash
sudo mkdir -p /opt/discord/releases
sudo mkdir -p /etc/discord-bot
sudo chown -R discord-bot:discord-bot /opt/discord
sudo chmod 755 /opt/discord
sudo chmod 755 /opt/discord/releases
```

GitLab Runner から `/opt/discord/releases` へ配置する場合は、Runner 実行ユーザーにも書き込み権限を付与します。

```bash
sudo setfacl -m u:gitlab-runner:rwx /opt/discord/releases
sudo setfacl -d -m u:gitlab-runner:rwx /opt/discord/releases
```

## 4. 環境変数ファイルを配置する

ソースリポジトリの `deploy/systemd/discord-bot.env.example` をコピーします。

```bash
sudo install -o root -g discord-bot -m 640 deploy/systemd/discord-bot.env.example /etc/discord-bot/discord-bot.env
sudo vi /etc/discord-bot/discord-bot.env
```

最低限、次の値を本番値に変更します。

| 変数 | 内容 |
|---|---|
| `DISCORD_TOKEN` | Discord Bot Token |
| `DB_USER` | DB ユーザー |
| `DB_PASSWORD` | DB パスワード |
| `DB_HOST` | DB ホスト |
| `DB_PORT` | DB ポート |
| `DB_NAME` | DB 名 |

`DB_HOST=localohst` のような typo は起動時にエラーになります。`localhost` または `127.0.0.1` を指定してください。

## 5. systemd unit を配置する

本番用 service を配置します。

```bash
sudo install -o root -g root -m 644 deploy/systemd/discord-bot.service /etc/systemd/system/discord-bot.service
sudo systemctl daemon-reload
```

開発用 service を利用する場合は、次を配置します。

```bash
sudo install -o root -g root -m 644 deploy/systemd/D_discord_dev.service /etc/systemd/system/D_discord_dev.service
sudo systemctl daemon-reload
```

## 6. 初回リリースを配置する

GitLab CI/CD でタグリリースする場合は、`DEPLOY_DIR=/opt/discord/releases` を CI/CD Variables に設定します。

手動配置する場合は、ソース一式を `/opt/discord/releases/<tag>` に配置します。

```bash
sudo mkdir -p /opt/discord/releases/v1.0.0
sudo rsync -a --exclude .git --exclude .venv --exclude cache --exclude files ./ /opt/discord/releases/v1.0.0/
sudo chown -R discord-bot:discord-bot /opt/discord/releases/v1.0.0
```

## 7. 仮想環境を作成する

```bash
sudo ln -sfn /opt/discord/releases/v1.0.0 /opt/discord/current
cd /opt/discord/current
sudo -u discord-bot python3 -m venv .venv
sudo -u discord-bot .venv/bin/python -m pip install --upgrade pip
sudo -u discord-bot .venv/bin/python -m pip install -r requirements.txt
sudo -u discord-bot .venv/bin/python -m pip check
```

## 8. 起動確認を行う

```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot --no-pager
```

ログで `DB initialized.`、`Cog initialize complete.`、`Bot ready:` が出力されることを確認します。

```bash
sudo journalctl -u discord-bot -n 100 --no-pager
```
