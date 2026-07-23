# systemd 実行設定

CentOS 上で Discord bot を systemd サービスとして実行するための設定ファイルです。

## ファイル

| ファイル | 配置先 | 用途 |
|---|---|---|
| `discord-bot.service` | `/etc/systemd/system/discord-bot.service` | systemd unit |
| `D_discord_dev.service` | `/etc/systemd/system/D_discord_dev.service` | 開発環境用 systemd unit |
| `discord-bot.env.example` | `/etc/discord-bot/discord-bot.env` | 環境変数ファイルのひな形 |
| `../scripts/release.sh` | 任意 | リリース切り替え用 shell |

## 前提

| 項目 | 値 |
|---|---|
| 実行ユーザー | `discord-bot` |
| リリース配置先 | `/opt/discord/releases/<tag>` |
| 実行対象 | `/opt/discord/current` |
| Python 仮想環境 | `/opt/discord/current/.venv` |

`/opt/discord/current` は、起動したいリリースディレクトリへのシンボリックリンクとして作成します。

```bash
sudo ln -sfn /opt/discord/releases/v1.0.0 /opt/discord/current
```

`/opt/discord/current` が既にディレクトリとして存在する場合、上記コマンドは `current` 自体をリンクにせず、`current/v1.0.0` というリンクを作成します。誤って作成した場合は、`current` ディレクトリを退避してからリンクを作り直してください。

```bash
cd /opt/discord
pwd
sudo mv /opt/discord/current /opt/discord/current.bak.$(date +%Y%m%d%H%M%S)
sudo ln -sfn /opt/discord/releases/v1.0.0 /opt/discord/current
ls -ld /opt/discord/current
```

正しい状態では、`ls -ld /opt/discord/current` の結果が `current -> /opt/discord/releases/v1.0.0` のようになります。

## 初回セットアップ

### 1. 実行ユーザー作成

```bash
sudo useradd --system --home-dir /opt/discord --shell /sbin/nologin discord-bot
```

既に別ユーザーで運用する場合は、`discord-bot.service` の `User` と `Group` を変更してください。
開発環境で `discord` ユーザーを利用する場合は、`D_discord_dev.service` を利用できます。

### 2. ディレクトリ作成

```bash
sudo mkdir -p /opt/discord/releases
sudo mkdir -p /etc/discord-bot
sudo chown -R discord-bot:discord-bot /opt/discord
sudo chmod 755 /opt/discord
sudo chmod 755 /opt/discord/releases
```

GitLab Runner が `/opt/discord/releases` にデプロイする場合は、Runner 実行ユーザーにも書き込み権限を付与してください。

```bash
sudo setfacl -m u:gitlab-runner:rwx /opt/discord/releases
sudo setfacl -d -m u:gitlab-runner:rwx /opt/discord/releases
sudo setfacl -m u:discord-bot:rwx /opt/discord/releases
sudo setfacl -d -m u:discord-bot:rwx /opt/discord/releases
```

タグ展開後のリリースディレクトリに対して、サービス実行ユーザーが `.venv`、`cache/`、`files/` を作成できる必要があります。

### 3. 環境変数ファイル配置

```bash
sudo install -o root -g discord-bot -m 640 deploy/systemd/discord-bot.env.example /etc/discord-bot/discord-bot.env
sudo vi /etc/discord-bot/discord-bot.env
```

`DISCORD_TOKEN`、DB 接続情報、外部サービス設定を実環境の値に変更してください。
地震情報と緊急地震速報は、`P2PQUAKE_MIN_NOTIFY_SCALE=40` により震度4以上のみ通知します。
画像内の日本語と記号を正しく表示するため、`P2PQUAKE_IMAGE_FONT_PATH` に日本語対応フォントを指定してください。

添付ファイル保存先は `MESSAGE_FILE_BASE_PATH` で指定します。相対パスの場合は `WorkingDirectory` である `/opt/discord/current` からの相対になります。

### 4. unit ファイル配置

```bash
sudo install -o root -g root -m 644 deploy/systemd/discord-bot.service /etc/systemd/system/discord-bot.service
sudo systemctl daemon-reload
```

開発環境用の unit を利用する場合は、次のように配置します。

```bash
sudo install -o root -g root -m 644 deploy/systemd/D_discord_dev.service /etc/systemd/system/D_discord_dev.service
sudo systemctl daemon-reload
```

### 5. Python 仮想環境作成

```bash
cd /opt/discord/current
sudo -u discord-bot python3 -m venv .venv
sudo -u discord-bot .venv/bin/python -m pip install --upgrade pip
sudo -u discord-bot .venv/bin/python -m pip install -r requirements.txt
```

## 起動・停止

```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot
```

停止と再起動:

```bash
sudo systemctl stop discord-bot
sudo systemctl restart discord-bot
```

ログ確認:

```bash
journalctl -u discord-bot -f
```

## リリース切り替え

新しいタグを `/opt/discord/releases/<tag>` に展開した後、`current` を差し替えて依存関係を更新し、サービスを再起動します。

リリース作業は `deploy/scripts/release.sh` でも実行できます。

```bash
sudo ./deploy/scripts/release.sh v1.0.1 discord-bot discord-bot
sudo ./deploy/scripts/release.sh v1.0.1 D_discord_dev discord
```

引数は `<tag> [service_name] [app_user]` です。
`APP_ROOT` を指定すると、既定の `/opt/discord` 以外にも配置できます。

```bash
sudo ln -sfn /opt/discord/releases/v1.0.1 /opt/discord/current
sudo chown -R discord-bot:discord-bot /opt/discord/releases/v1.0.1
ls -ld /opt/discord/current
cd /opt/discord/current
test -f requirements.txt
sudo -u discord-bot python3 -m venv .venv
sudo -u discord-bot .venv/bin/python -m pip install --upgrade pip
sudo -u discord-bot .venv/bin/python -m pip install -r requirements.txt
sudo systemctl restart discord-bot
```

## 画像用フォントの配置

地震・津波画像の日本語や記号が文字化けする場合は、日本語対応フォントを配置して `P2PQUAKE_IMAGE_FONT_PATH` に指定します。

```bash
sudo mkdir -p /opt/discord/fonts
sudo cp /path/to/NotoSansCJKjp-Regular.otf /opt/discord/fonts/NotoSansCJKjp-Regular.otf
sudo chown -R discord:discord /opt/discord/fonts
```

本番環境で `discord-bot` ユーザーを利用している場合は、`chown` のユーザーとグループを `discord-bot:discord-bot` に読み替えてください。
OS パッケージで日本語フォントを導入済みの場合は、`/usr/share/fonts/...` 配下の実ファイルを `P2PQUAKE_IMAGE_FONT_PATH` に指定しても問題ありません。

`/etc/discord-bot/discord-bot.env` に次の設定を追加または確認してください。

```env
P2PQUAKE_IMAGE_FONT_PATH=/opt/discord/fonts/NotoSansCJKjp-Regular.otf
```

設定後はサービスを再起動します。

```bash
sudo systemctl restart D_discord_dev.service
```

## 地理院タイルの事前キャッシュ

地震・津波画像の背景地図は地理院タイルを利用します。
初回通知時の外部通信失敗や遅延を避けるため、運用開始前に日本周辺のタイルをキャッシュできます。

```bash
cd /opt/discord/current
sudo -u discord .venv/bin/python deploy/scripts/cache_gsi_tiles.py
```

既定では `/opt/discord/current/cache/gsi_tiles` に、日本周辺の `zoom=5,6,7` を保存します。
保存先を変更する場合は、systemd の環境変数 `GSI_TILE_CACHE_DIR` と同じ値を指定してください。

```bash
sudo -u discord .venv/bin/python deploy/scripts/cache_gsi_tiles.py \
  --cache-dir /opt/discord/current/cache/gsi_tiles \
  --zoom 5 6 7
```

取得対象の確認だけを行う場合は `--dry-run` を使用します。

```bash
sudo -u discord .venv/bin/python deploy/scripts/cache_gsi_tiles.py --dry-run
```

## 権限確認

```bash
sudo -u discord-bot test -r /etc/discord-bot/discord-bot.env && echo env-readable
sudo -u discord-bot test -x /opt/discord/current/.venv/bin/python && echo python-ready
sudo -u discord-bot test -w /opt/discord/current && echo app-dir-writable
```

`cache/` や `files/` を利用するため、実行ユーザーが `/opt/discord/current` 配下へ書き込める必要があります。

## トラブルシューティング

### `status=217/USER` で起動できない

`status=217/USER` は、systemd が unit の `User` または `Group` に指定されたユーザーへ切り替えられない場合に発生します。
サービスが Python を実行する前に失敗しているため、アプリケーションコードや `.venv` の問題ではありません。

unit の実行ユーザーを確認します。

```bash
sudo systemctl cat D_discord_dev.service
id discord
id discord-bot
```

開発環境で `discord` ユーザーを使う場合は、unit を次の設定に揃えてください。

```ini
User=discord
Group=discord
```

修正後は systemd を再読み込みして再起動します。

```bash
sudo systemctl daemon-reload
sudo systemctl restart D_discord_dev.service
sudo systemctl status D_discord_dev.service
```

### `status=1/FAILURE` で起動できない

`status=1/FAILURE` は、systemd から Python は起動できていますが、アプリケーション起動中に例外が発生して終了している状態です。
まず journal の末尾で Python の例外本文を確認します。

```bash
sudo journalctl -u D_discord_dev.service -n 100 --no-pager
```

手動実行でも同じエラーを確認できます。

```bash
cd /opt/discord/current
sudo -u discord /opt/discord/current/.venv/bin/python -u /opt/discord/current/main.py
```

よくある原因は次の通りです。

| 原因 | 確認コマンド |
|---|---|
| `DISCORD_TOKEN` が未設定 | `sudo systemctl show D_discord_dev.service -p EnvironmentFiles` |
| 環境変数ファイルが読めない | `sudo -u discord test -r /etc/discord-bot/discord-bot.env && echo env-readable` |
| MySQL に接続できない | `mysql -h 127.0.0.1 -u discord_bot -p discord_bot` |
| `DB_HOST` の typo | `sudo grep '^DB_HOST=' /etc/discord-bot/discord-bot.env` |
| `requirements.txt` の依存関係が不足 | `cd /opt/discord/current && sudo -u discord .venv/bin/python -m pip check` |

`DB_HOST=localohst` のような typo がある場合は、`localhost` または `127.0.0.1` に修正してください。
