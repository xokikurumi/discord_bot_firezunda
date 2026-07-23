# コミュニケーション傾向分析

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-005 |
| 処理名 | コミュニケーション傾向分析 |
| 実装 | `cogs/tasks/communication_trend_cog.py`、`services/task/communication_trend_service.py` |
| 実行方式 | 定期処理・手動実行 |
| 手動コマンド | `!communication_trend_analyze`、`/communication_trend_analyze` |

## 2. 処理概要

メッセージログ、編集ログ、削除ログ、Ollama 分析ログを集計し、Ollama により半期ごとの傾向レポートを生成します。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `COMMUNICATION_TREND_ANALYSIS_ENABLED=true` |
| チェック間隔 | `COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS` 秒 |
| ユーザー分析最小メッセージ数 | `COMMUNICATION_TREND_MIN_USER_MESSAGES` |
| サンプル上限 | `COMMUNICATION_TREND_SAMPLE_LIMIT` |
| Ollama URL | `OLLAMA_URL` |
| Ollama model | `OLLAMA_MODEL` |

## 4. 定期実行条件

| 実行日 JST | 分析対象期間 |
|---|---|
| 1 月 1 日 | 前年 6 月 1 日から当年 1 月 1 日 |
| 6 月 1 日 | 当年 1 月 1 日から当年 6 月 1 日 |

手動実行時は、直近の完了済み分析期間を対象にします。

## 5. 処理詳細

1. 対象期間を判定する。
2. 対象 guild を `message_log` から抽出する。
3. guild 単位分析が有効な場合、guild レポートを生成する。
4. 対象 user をメッセージ数条件で抽出する。
5. メッセージ数、編集数、削除数、分析スコア、サンプル本文を集計する。
6. Ollama に JSON 形式の傾向レポート生成を依頼する。
7. `communication_trend_analysis` に upsert する。

## 6. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | `message_log`、`message_edit_log`、`message_delete_log`、`message_analysis_log` |
| 外部連携 | Ollama chat API |
| 出力 | `communication_trend_analysis` |

## 7. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| レポートが生成されない | 対象期間の `message_log` 件数を確認する |
| Ollama 失敗 | `OLLAMA_URL`、`OLLAMA_MODEL`、タイムアウトを確認する |
| 同じ期間が再生成される | 既存 row の `summary` が `Ollama analysis failed.` になっていないか確認する |
