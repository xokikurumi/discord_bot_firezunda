# 運用設計

| 項目 | 内容 |
|---|---|
| 起動 | `python main.py` で起動する。 |
| 停止 | プロセス停止時に DB engine を dispose する。 |
| リリース | GitLab のタグ pipeline で `DEPLOY_DIR/<tag>` へ展開する。 |
| 監視 | 標準出力ログに起動、同期、通知、エラー情報を出力する。 |
| 設定変更 | 環境変数変更後、Bot を再起動する。 |

## CI/CD

- `python_compile` で依存関係導入と Python 構文チェックを実行する。
- `deploy_release` は Git tag のみで実行する。
- ホストディレクトリへ反映する場合は Shell executor Runner を利用する。
