# 制約・前提条件

## 1. 外部サービス制約

| ID | 制約 |
|---|---|
| CON-EXT-001 | Discord API の仕様、権限、Rate Limit の影響を受ける。 |
| CON-EXT-002 | P2PQuake、Geolonia、気象庁関連ページ、Niconico、Ollama、ICS 配信元の仕様変更の影響を受ける。 |
| CON-EXT-003 | slash command の反映には Discord 側の同期時間がかかる場合がある。 |

## 2. 環境制約

| ID | 制約 |
|---|---|
| CON-ENV-001 | DB は MySQL 互換の接続先を前提とする。 |
| CON-ENV-002 | 運用環境では Discord Bot と外部サービスへ到達できるネットワークが必要である。 |
| CON-ENV-003 | CI/CD Runner はドキュメント検証とリリース処理に必要なコマンドを実行できる必要がある。 |

## 3. 文書化制約

| ID | 制約 |
|---|---|
| CON-DOC-001 | ドキュメントは Markdown 形式、UTF-8 で管理する。 |
| CON-DOC-002 | テーブル定義はテーブルごと、詳細設計は機能ごとに分割する。 |
| CON-DOC-003 | 要件、設計、バッチ、テーブル定義の粒度を対応付けられるようにする。 |
