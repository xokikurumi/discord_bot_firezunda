# セキュリティ設計

| 項目 | 方針 |
|---|---|
| 秘密情報 | token、DB パスワードは環境変数または GitLab CI/CD Variables で管理する。 |
| 管理コマンド | Discord 管理者権限を要求する。 |
| 通知先制御 | ギルド単位・カテゴリ単位の通知先設定で投稿先を制御する。 |
| URL 文脈取得 | メッセージ分析用のリンク先取得は HTTP/HTTPS、標準 port、公開 IP、許可 content type のみ許可する。 |
| リダイレクト制御 | リダイレクト先も URL 安全確認を行い、localhost、private address、userinfo、非標準 port を拒否する。 |
| CI/CD デプロイ | Shell executor Runner と `DEPLOY_DIR` 権限によりホスト反映先を制御する。 |

## 注意事項

- Discord token が漏洩した場合は速やかに再生成する。
- `.env` やキャッシュ、添付ファイル保存先は Git 管理対象外とする。
