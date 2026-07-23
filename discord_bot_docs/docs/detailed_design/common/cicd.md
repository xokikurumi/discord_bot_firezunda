# CI/CD 詳細

## 対象ファイル

| ファイル | 内容 |
|---|---|
| `.gitlab-ci.yml` | GitLab CI/CD 定義 |
| `requirements.txt` | Python 依存関係 |

## ジョブ

| ジョブ | ステージ | 実行条件 | 内容 |
|---|---|---|---|
| `python_compile` | `test` | 通常 pipeline | venv 作成、依存導入、`compileall` 実行 |
| `deploy_release` | `deploy` | Git tag pipeline | `DEPLOY_DIR/<tag>` に checkout 済みソースを展開 |

## Runner 条件

| 項目 | 内容 |
|---|---|
| tag | `shell` |
| executor | Shell executor 推奨 |
| deploy 権限 | `DEPLOY_DIR` に Runner 実行ユーザーが書き込めること |

## deploy ガード

| チェック | 失敗条件 |
|---|---|
| `CI_COMMIT_TAG` | タグ pipeline ではない |
| `DEPLOY_DIR` | 未設定 |
| Docker executor | `/.dockerenv` が存在する |
| 絶対パス | `DEPLOY_DIR` が `/` で始まらない |
| 書き込み権限 | `DEPLOY_DIR` が存在しない、または書き込めない |
