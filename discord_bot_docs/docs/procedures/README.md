# 手順書一覧

Discord bot の運用手順書です。

## 対象システム

| 項目 | 内容 |
|---|---|
| アプリケーション | Discord bot |
| 実行方式 | Python + systemd |
| 主要配置先 | `/opt/discord` |
| 稼働リンク | `/opt/discord/current` |
| リリース配置先 | `/opt/discord/releases/<tag>` |
| 環境変数ファイル | `/etc/discord-bot/discord-bot.env` |
| systemd service | `discord-bot.service` |

## 手順書

- [初期セットアップ手順](initial_setup.md)
- [リリース手順](release.md)
- [サービス運用手順](service_operation.md)
- [切り戻し手順](rollback.md)
- [保守・確認手順](maintenance.md)

## 前提

- Python 3.10 以上が利用できること。
- MySQL または MariaDB が利用できること。
- Discord Bot Token を取得済みであること。
- 本番配置では systemd を利用すること。
- GitLab CI/CD でタグリリースする場合は Shell executor の Runner を利用すること。
