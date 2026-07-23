# Ollama メッセージ分析

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-008 |
| 処理名 | Ollama メッセージ分析 |
| 実装 | `cogs/messages/base/message_watcher_cog.py`、`services/base/messageWatcherService.py` |
| 実行方式 | イベント駆動非同期処理 |
| 起動契機 | Discord メッセージ投稿時 |

## 2. 処理概要

ユーザーが投稿したサーバーメッセージを非同期 task として分析し、Ollama の判定結果を DB に保存します。
スコアが閾値以上の場合はリアクション付与や DM 通知を行います。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `OLLAMA_ANALYSIS_ENABLED=true` |
| 対象外 | Bot 投稿、DM、空メッセージ、`!` で始まるコマンド |
| 同時実行数 | `OLLAMA_MAX_CONCURRENCY` |
| リアクション閾値 | `OLLAMA_REACTION_THRESHOLD` |
| DM 閾値 | `OLLAMA_DM_THRESHOLD` |

## 4. 処理詳細

1. `on_message` でユーザーメッセージを検知する。
2. `asyncio.create_task` で分析処理を起動する。
3. 直近の文脈メッセージを `message_log` から取得する。
4. Ollama chat API に JSON 形式の分析を依頼する。
5. `aggression`、`intimidation`、`insult`、`sarcasm`、`snide`、`discomfort` を 0 から 100 に正規化する。
6. `message_analysis_log` に保存する。
7. 閾値以上の場合は `✖` リアクションを付与する。
8. DM 閾値以上の場合は投稿者へ DM する。

## 5. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | Discord 投稿メッセージ、`message_log` の直近文脈 |
| 外部連携 | Ollama chat API |
| 出力 | `message_analysis_log`、リアクション、DM |

## 6. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 分析されない | `OLLAMA_ANALYSIS_ENABLED` と対象外条件を確認する |
| Ollama 失敗 | `OLLAMA_URL`、`OLLAMA_MODEL`、タイムアウトを確認する |
| DM が届かない | ユーザーの DM 受信設定を確認する |
