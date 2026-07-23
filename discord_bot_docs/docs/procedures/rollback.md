# 切り戻し手順

## 1. 切り戻し方針

リリースは `/opt/discord/current` のシンボリックリンクで切り替えています。
切り戻しは、`current` を正常稼働していた過去タグへ戻して service を再起動します。

## 2. 現在の稼働バージョンを確認する

```bash
ls -ld /opt/discord/current
sudo systemctl status discord-bot --no-pager
```

例として、現在 `v1.0.1` が稼働しており、`v1.0.0` へ戻す場合を示します。

## 3. 切り戻し先を確認する

```bash
test -d /opt/discord/releases/v1.0.0
test -f /opt/discord/releases/v1.0.0/main.py
test -f /opt/discord/releases/v1.0.0/requirements.txt
```

## 4. release.sh で切り戻す

過去タグのディレクトリに含まれる `release.sh` を使って切り替えます。

```bash
cd /opt/discord/releases/v1.0.0
sudo ./deploy/scripts/release.sh v1.0.0 discord-bot discord-bot
```

この方法では、切り戻し先の `.venv` 作成、依存関係更新、`pip check`、service restart まで実行されます。

## 5. 手動で切り戻す

`release.sh` が使えない場合の手動手順です。

```bash
sudo ln -sfn /opt/discord/releases/v1.0.0 /opt/discord/current
sudo chown -R discord-bot:discord-bot /opt/discord/releases/v1.0.0
cd /opt/discord/current
sudo -u discord-bot python3 -m venv .venv
sudo -u discord-bot .venv/bin/python -m pip install --upgrade pip
sudo -u discord-bot .venv/bin/python -m pip install -r requirements.txt
sudo -u discord-bot .venv/bin/python -m pip check
sudo systemctl restart discord-bot
```

## 6. 切り戻し後確認

```bash
ls -ld /opt/discord/current
sudo systemctl status discord-bot --no-pager
sudo journalctl -u discord-bot -n 100 --no-pager
```

Discord 側で代表コマンドを確認します。

```text
/roll expression:1d20
/notify_config category list
```

## 7. DB 変更を含む場合の注意

起動時 migration は不足カラム追加や index 調整を行います。
過去バージョンへ戻す場合、DB schema が新バージョン向けに進んだ状態で稼働する可能性があります。

切り戻し前に、該当リリースで互換性のない DB 変更がないか確認してください。
互換性がない場合は、DB バックアップからの復元または個別の逆 migration を検討します。

## 8. 切り戻し完了条件

- `/opt/discord/current` が切り戻し先タグを指していること。
- systemd service が `active (running)` であること。
- journal に起動エラーがないこと。
- Discord 上で代表コマンドが応答すること。
