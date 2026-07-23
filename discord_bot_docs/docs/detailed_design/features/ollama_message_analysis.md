# Ollama メッセージ分析詳細

## 1. 目的

ユーザー投稿を Ollama chat API に送信し、攻撃性、威圧、侮辱、皮肉、嫌味、不快可能性を採点する。
各スコアは 0 から 100 とする。
しきい値に応じて投稿へ検出リアクションを付け、通知チャンネルと投稿者 DM に通知する。
管理者フィードバックを蓄積し、類似する確認済み事例を動的 few-shot として分析時に参照する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| MessageWatcherCog | 投稿 listener から分析タスクを起動する |
| AnalysisCog | 管理者フィードバックコマンドを提供する |
| MessageWatcherService | Ollama 呼び出し、RAG 事例取得、結果正規化、保存、通知を行う |
| MessageAnalysisLogRepository | 分析結果を message id で insert ignore し、message id で取得する |
| MessageAnalysisFeedbackRepository | 管理者レビュー結果の保存と RAG 候補取得を行う |
| MessageLogRepository | 直近文脈と対象 message の guild 整合性確認に使用する |

## 3. 投稿分析 listener

1. `on_message` が発火する。
2. Bot 投稿は無視する。
3. DM は無視する。
4. `asyncio.create_task` でバックグラウンド分析を起動する。
5. 分析タスク内例外は message id 付きでログ出力する。

## 4. 分析対象条件

Service の `watch` は次を満たさない場合 `None` を返す。

| 条件 | 無視条件 |
|---|---|
| 機能有効 | `OLLAMA_ANALYSIS_ENABLED` が false |
| content | 空 |
| command 風 | `!` で始まる |

## 5. 文脈取得

対象 message の channel id と message id を使い、同一 channel の直近 10 件を取得する。
文脈は古い順の行を `user:{user_id}: {content}` 形式にし、改行を空白へ変換する。
文脈がない場合は `(no previous messages)` とする。

## 6. Ollama リクエスト

HTTP はブロッキング API のため `asyncio.to_thread` で実行し、同時実行数は `OLLAMA_MAX_CONCURRENCY` の semaphore で制限する。

リクエスト前に、同一 guild の管理者確認済みフィードバックから類似事例を取得する。取得後、リクエスト payload は以下とする。

| 項目 | 値 |
|---|---|
| model | `OLLAMA_MODEL` |
| stream | false |
| format | `json` |
| options.temperature | 0 |
| options.num_predict | `OLLAMA_NUM_PREDICT` |
| messages[0] | system prompt |
| messages[1..n] | few-shot examples |
| messages[n+1..m] | 管理者フィードバック RAG examples |
| last user message | user prompt template に context と target を埋め込んだ文字列 |

対象本文は `OLLAMA_MESSAGE_MAX_CHARS` で後方切り詰める。
文脈は `OLLAMA_CONTEXT_MAX_CHARS` で後方切り詰める。
Ollama が length 起因の空応答を返した場合は `OLLAMA_RETRY_CONTEXT_MAX_CHARS` で再試行する。

## 7. few-shot

few-shot JSON は配列のみ有効とする。
各要素は `input` または `message`、`output` または `judgment` を持つ dict とする。
最大件数は `OLLAMA_ANALYSIS_FEWSHOT_MAX_EXAMPLES`。output は通常結果と同じ正規化を通す。

## 8. フィードバック RAG

RAG が無効、guild id がない、候補数または最大採用数が 0 以下の場合は空配列を返す。

候補は同一 guild の確認済みフィードバックから取得する。
条件は `review_status=CONFIRMED`、`corrected_result_json` が空でないこと。
対応する message content が空でない行を、作成日時と id の降順で最大候補数まで取得する。

対象検索文は、対象メッセージ、直前会話の末尾 5 件、対象メッセージが 12 文字以下の場合の `補足: 短文` で構成する。候補検索文は、過去の対象メッセージ、管理者判断 label、note で構成する。

類似度は次の軽量特徴で算出する。

1. 英数字と日本語連続文字を token 化する。
2. 空白を除去した文字列から 2-gram と 3-gram を追加する。
3. 3 文字以下の短文では 1 文字 token も追加する。
4. 左右 token の積集合数を、左右 token 数の小さい方で割り、100 倍して四捨五入する。

類似度が `OLLAMA_ANALYSIS_FEEDBACK_RAG_MIN_SIMILARITY` 未満の候補は除外する。
補正 JSON を正規化できない候補も除外する。
残った候補を類似度降順に並べ、最大 `OLLAMA_ANALYSIS_FEEDBACK_RAG_MAX_EXAMPLES` 件採用する。

採用例は prompt に次の形で追加する。

| role | content |
|---|---|
| user | 管理者確認済みの動的参考事例を使うが、機械的にコピーしない旨の説明 |
| user | 例番号、類似度、label に基づく context、対象メッセージ、note、過去分析スコア |
| assistant | 補正済み結果 JSON |

## 9. JSON 解析

Ollama の assistant content を取得する。
空の場合は done reason または error を含む `ValueError` とする。
content が Markdown code fence の場合は fence を除去する。
通常 JSON parse に失敗した場合は、最初の balanced JSON object を抽出して再 parse する。

## 10. 結果正規化

| 項目 | 正規化 |
|---|---|
| aggression/intimidation/insult/sarcasm/snide/discomfort | int 化し 0 から 100 に clamp |
| targeted | bool、既定 true |
| confidence | int 化し 0 から 100 に clamp |
| context_dependency | bool、既定 false |
| reason | strip 済み文字列 |

bool は bool、数値、`true/1/yes/y/on`、`false/0/no/n/off` を解釈する。

## 11. 判定

`max_score` は 6 スコアすべての最大値。通知判定用スコアは aggression、intimidation、insult、discomfort の最大値。

| 判定 | 条件 |
|---|---|
| should_react | 通知判定用スコアが `OLLAMA_REACTION_THRESHOLD` 以上 |
| should_notify | 通知判定用スコアが `OLLAMA_DM_THRESHOLD` 以上 |

ただし confidence が `OLLAMA_CONFIDENCE_THRESHOLD` 未満なら false。
targeted が true なら alert 可。
targeted が false の場合は intimidation が 80 以上のときのみ alert 可。

## 12. 保存

分析結果は message id 単位で insert ignore する。
保存項目は message/guild/channel/user/model、6 スコア、max score、targeted、confidence とする。
context dependency、reason、raw result JSON、prompt version、prompt hash も保存する。
参照 RAG 事例 JSON、should_react、should_notify も保存する。

prompt version は `OLLAMA_ANALYSIS_PROMPT_VERSION` を使用する。
prompt hash は Ollama に送信する messages を key sort 付き JSON にする。
その UTF-8 bytes の SHA-256 hex digest とする。
参照 RAG 事例は case id、similarity、label の配列として保存する。

保存済み message の再分析では Bot 投稿、空 content、`!` 始まりを無視し、リアクションと DM は行わない。

## 13. 通知

should_react が true の場合、対象 message に `✖` リアクションを追加する。
失敗はログ出力のみ。
さらに通知チャンネル id が設定されている場合、Bot cache または fetch で channel を取得する。
guild id 設定がある場合は channel guild と一致するか確認して送信する。

should_notify が true の場合、投稿者へ日本語 DM を送信する。DM 失敗はログ出力のみ。

## 14. フィードバック

`analysis feedback <message_id> <label> [note]` は guild 限定、管理者のみ。
message id は decimal 文字列のみ受け付ける。
保存済み message が別 guild の場合はエラーにする。

label alias は次の通り。

| 入力 | 保存値 |
|---|---|
| `ok`、`correct`、`true`、`正しい` | `correct` |
| `fp`、`false_positive`、`誤検知` | `false_positive` |
| `fn`、`false_negative`、`見逃し` | `false_negative` |
| `unsure`、`unknown`、`不明` | `unsure` |

フィードバック登録時は、対象 message が別 guild に属していればエラーにする。既存分析結果がある場合は message id で取得する。

補正結果は次の優先順で作成する。

1. note に JSON object が含まれる場合、最初の balanced JSON object を抽出して分析結果スキーマで正規化する。
2. label が `correct` で既存分析結果がある場合、既存分析結果を補正結果として保存する。
3. label が `false_positive` の場合、6 スコアを低くした過検出補正結果を保存する。
4. 上記以外は補正結果なしとする。

補正結果がある場合は `review_status=CONFIRMED` とする。
補正結果がない場合は `review_status=PENDING` とする。
保存項目は message/guild/channel/user/reviewer、label、review status、corrected result JSON、note とする。
