# リリース切り替え

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-010 |
| 処理名 | リリース切り替え |
| 実装 | `deploy/scripts/release.sh` |
| 実行方式 | 手動スクリプト |
| 起動契機 | 運用者実行 |

## 2. 処理概要

`/opt/discord/releases/<tag>` に配置済みのリリースを `/opt/discord/current` へ切り替え、Python 依存関係を更新して systemd service を再起動します。

## 3. 実行例

```bash
cd /opt/discord/releases/v1.0.0
sudo ./deploy/scripts/release.sh v1.0.0 discord-bot discord-bot
```

開発用 service の例です。

```bash
sudo ./deploy/scripts/release.sh v1.0.0 D_discord_dev discord
```

## 4. 処理詳細

1. root 実行であることを確認する。
2. アプリ実行ユーザーが存在することを確認する。
3. リリースディレクトリ、`requirements.txt`、`main.py` の存在を確認する。
4. `/opt/discord/current` が通常ファイルまたはディレクトリの場合は退避する。
5. `/opt/discord/current` を対象リリースへシンボリックリンクする。
6. 所有者をアプリ実行ユーザーへ変更する。
7. `.venv` を作成または再利用する。
8. pip と依存関係を更新する。
9. `pip check` を実行する。
10. systemd service を restart する。

## 5. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| root エラー | `sudo` で実行しているか確認する |
| release directory なし | GitLab CI/CD の配置結果を確認する |
| service restart 失敗 | `journalctl -u <service>` を確認する |
