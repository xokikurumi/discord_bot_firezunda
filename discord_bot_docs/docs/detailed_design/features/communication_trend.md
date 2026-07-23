# コミュニケーション傾向分析詳細

## 1. 目的

メッセージログ、編集ログ、削除ログ、Ollama 分析ログを半期単位で集計し、guild または user 単位の日本語レポートを Ollama で生成して保存する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| CommunicationTrendCog | background task と手動分析コマンドを提供する |
| CommunicationTrendService | 期間算出、集計、Ollama レポート生成、保存を行う |
| CommunicationTrendAnalysisRepository | 期間/scope/guild/user 単位の取得と upsert を行う |
| TrendPeriod | `key`、UTC `start`、UTC `end` を持つ半期期間 |

## 3. 起動と停止

Cog load 時に task が未作成または完了済みなら `run_forever` を `asyncio.create_task` で開始する。Cog unload 時は task を cancel する。

## 4. 定期実行

機能が無効な場合は開始ログを出して終了する。有効な場合は Bot ready を待ち、`COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS` ごとに判定する。

| 日付 JST | 対象期間 |
|---|---|
| 1 月 1 日 | 前年 6 月 1 日 00:00 JST から 当年 1 月 1 日 00:00 JST |
| 6 月 1 日 | 当年 1 月 1 日 00:00 JST から 当年 6 月 1 日 00:00 JST |

同一期間 key は `last_run_key` でプロセス内重複実行を防ぐ。

## 5. 手動コマンド

`communication_trend_analyze` は guild 限定、管理者のみ。
最新の完了済み定期対象期間を現在日付から計算し、現在 guild のみ分析する。
slash interaction では ephemeral、prefix command では 10 秒後削除の status を送信する。

## 6. 期間 key

期間 key は `{start_year}-{start_month}_to_{end_year}-{end_month}` 形式とする。開始/終了は JST 境界で作成してから UTC に変換して DB 条件に使用する。

## 7. 対象 guild/user

guild id は対象期間内の `message_log` から、Bot 投稿を除き distinct で取得する。
user id は guild 内で Bot 投稿を除いた message count が設定値以上のユーザーを取得する。
取得順は message count 降順とする。

## 8. 分析スコープ

`COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED` が true の場合は guild 単位も分析する。user 単位は常に対象 user を順に分析する。

既存レポートが存在し、summary が `Ollama analysis failed.` ではない場合は再生成しない。失敗レポートは再試行対象とする。

## 9. 集計指標

対象期間、guild、任意 user 条件で次を集計する。

| 指標 | 取得元 |
|---|---|
| message_count | `message_log` count |
| active_user_count | `message_log` distinct user count |
| attachment_count | `message_log.has_attachments` sum |
| embed_count | `message_log.has_embeds` sum |
| sticker_count | `message_log.has_stickers` sum |
| edit_count | `message_edit_log` count |
| delete_count | `message_delete_log` count |
| analysis_count | `message_analysis_log` count |
| max_score_avg | `message_analysis_log.max_score` average rounded |
| analysis_averages | 6 スコアの average、小数 1 桁 |
| reacted_count | `should_react` sum |
| notified_count | `should_notify` sum |
| samples | 対象期間の最新メッセージ本文、最大 `COMMUNICATION_TREND_SAMPLE_LIMIT` 件 |

サンプル本文は改行を空白にし、200 文字を超える場合は先頭 200 文字に `...` を付与する。

## 10. Ollama レポート

リクエストは thread で実行する。payload は model、stream false、format json、temperature 0 を指定する。
`COMMUNICATION_TREND_NUM_PREDICT` も payload に設定する。
system prompt は、性格や健康診断を避けるよう指示する。
分析対象は観測可能なコミュニケーション傾向、運用、摩擦シグナル、改善案に限定する。

user message は scope_type、period_key、period_start、period_end、metrics を JSON 文字列化して渡す。
応答 JSON は `summary`、`tendencies`、`risks`、`recommendations` を想定する。

空応答の場合は samples を先頭 5 件に減らして再試行する。HTTP、URL、timeout、JSON、値エラーは失敗レポートに変換する。

## 11. 保存

保存時は period、scope、guild、user、model、主要 count、metrics JSON を upsert する。
summary、tendencies、risks、recommendations、raw result JSON も保存する。
list は改行結合、dict は JSON 文字列、その他は文字列化して保存する。
