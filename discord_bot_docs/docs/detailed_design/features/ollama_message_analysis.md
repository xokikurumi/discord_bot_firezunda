# Ollama メッセージ分析詳細

## 1. 目的

ユーザー投稿を Ollama chat API に送信し、攻撃性、威圧、侮辱、皮肉、嫌味、不快可能性を採点する。
各スコアは 0 から 100 とする。
しきい値に応じて投稿へ検出リアクションを付け、通知チャンネルと投稿者 DM に通知する。
管理者フィードバックを蓄積し、本文完全一致または類似する確認済み事例を分析時に参照する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| MessageWatcherCog | 投稿 listener から分析タスクを起動する |
| AnalysisCog | 管理者フィードバックコマンドとホワイトリスト管理コマンドを提供する |
| MessageWatcherService | Ollama 呼び出し、ホワイトリスト判定、投稿者文脈取得、完全一致フィードバック取得、RAG 事例取得、URL 文脈取得、結果正規化、保存、通知を行う |
| MessageAnalysisLogRepository | 分析結果を message id で insert ignore し、message id で取得する |
| MessageAnalysisFeedbackRepository | 管理者レビュー結果の保存、embedding 保存、本文完全一致結果取得、RAG 候補取得を行う |
| MessageAnalysisWhitelistRepository | guild 単位の分析除外ルールを保存、一覧取得、有効/無効切替する |
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
| whitelist | 有効な分析除外ルールに一致する |

## 5. 文脈取得

対象 message の channel id と message id を使い、同一 channel の直近 10 件を取得する。
文脈は古い順の行を `user:{user_id}: {content}` 形式にし、改行を空白へ変換する。
文脈がない場合は `(no previous messages)` とする。

通常の Discord message では、対象投稿者から guild 表示名、global 名、ユーザー名、discriminator を組み立てる。
保存済み message の再分析では、`discord_user` の保存済み行があれば同じ形式で投稿者文脈を組み立てる。
投稿者文脈は対象メッセージ本文ではなく、名前由来の誤読を避けるための補助情報として prompt に渡す。

## 6. 解析設定

| 設定 | 既定値 | 用途 |
|---|---|---|
| `OLLAMA_ANALYSIS_SYSTEM_PROMPT_PATH` | `config/analysis_system_prompt.md` | system prompt の Markdown ファイル |
| `OLLAMA_ANALYSIS_SYSTEM_PROMPT` | 空 | system prompt を環境変数で直接指定する |
| `OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE` | 既定 template | user prompt template |
| `OLLAMA_ANALYSIS_FEWSHOT_PATH` | `config/analysis_fewshot_examples.json` | 固定 few-shot JSON ファイル |
| `OLLAMA_ANALYSIS_FEWSHOT_MAX_EXAMPLES` | `10` | 固定 few-shot の最大投入件数 |
| `OLLAMA_ANALYSIS_FEEDBACK_RAG_ENABLED` | true | 管理者 feedback RAG の有効化 |
| `OLLAMA_ANALYSIS_FEEDBACK_RAG_CANDIDATE_LIMIT` | `50` | RAG 候補取得の最小 scan 件数 |
| `OLLAMA_ANALYSIS_FEEDBACK_RAG_SEARCH_POOL_LIMIT` | `2000` | 類似事例探索用の拡張 scan 件数 |
| `OLLAMA_ANALYSIS_FEEDBACK_RAG_MAX_EXAMPLES` | `3` | prompt に投入する RAG 事例数 |
| `OLLAMA_ANALYSIS_FEEDBACK_RAG_MIN_SIMILARITY` | `25` | RAG 採用の最小類似度 |
| `OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_RAG_ENABLED` | false | embedding 類似度利用の有効化 |
| `OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_MIN_SIMILARITY` | `60` | embedding 類似度の最小採用値 |
| `OLLAMA_EMBEDDING_URL` | chat URL から `/api/embed` を導出 | embedding API URL |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text:latest` | embedding model |
| `OLLAMA_EMBEDDING_TIMEOUT_SECONDS` | `60` | embedding API timeout |
| `OLLAMA_ANALYSIS_URL_CONTEXT_ENABLED` | true | URL 文脈取得の有効化 |
| `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CONCURRENCY` | `1` | URL 文脈取得の同時実行数 |
| `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_URLS` | `2` | 1 message あたりの URL 取得件数 |
| `OLLAMA_ANALYSIS_URL_CONTEXT_TIMEOUT_SECONDS` | `5` | URL 取得 timeout |
| `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_BYTES` | `200000` | URL 応答読み込み byte 上限 |
| `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CHARS` | `2000` | prompt に渡す URL 文脈文字数 |
| `OLLAMA_ANALYSIS_MEME_GUARD_ENABLED` | true | ミーム曖昧性ガードの有効化 |
| `OLLAMA_ANALYSIS_MEME_GUARD_SCORE_CAP` | `40` | ガード適用時の 6 スコア上限 |
| `OLLAMA_ANALYSIS_MEME_GUARD_CONFIDENCE_CAP` | `65` | ガード適用時の confidence 上限 |

system prompt は環境変数の直接指定を最優先する。
空の場合は prompt path のファイルを UTF-8 で読み込み、読み込めない場合は既定 prompt を使用する。
prompt file は相対 path の場合、プロセスの working directory から解決する。

## 7. 分析実行順序

分析は次の順序で実行する。

1. 同一 guild の確認済みフィードバックから、対象本文と完全一致する補正結果を取得する。
2. 完全一致結果があれば Ollama へ送信せず、その補正結果を分析結果として返す。
3. 完全一致結果がなければ、確認済みフィードバックの類似事例を取得する。
4. 対象本文に含まれる URL から、安全に取得できるリンク先文脈を作成する。
5. 同時実行 semaphore を取得し、Ollama リクエストを実行する。
6. ミーム曖昧性ガードを適用し、必要に応じて alert しきい値未満へ抑制する。
7. RAG 過検出ガードを適用し、高類似の過検出補正事例に基づいて再過検出を抑制する。

完全一致フィードバック取得、類似事例取得、URL 文脈取得のいずれかで例外が発生しても、分析全体は停止せずログ出力後に利用可能な情報だけで継続する。

ホワイトリスト判定に一致した場合は上記の分析順序には進まず、分析結果保存、リアクション、DM 通知を行わない。

## 8. 完全一致フィードバック

同一 guild の確認済みフィードバックから、対象本文と完全一致する補正結果を取得する。

取得条件は次の通り。

| 項目 | 条件 |
|---|---|
| guild | 対象メッセージと同一 guild |
| review status | `CONFIRMED` |
| corrected result | null でも空文字でもない |
| message content | trim 後の本文が対象本文と完全一致 |
| 並び順 | 作成日時降順、id 降順 |
| 件数 | 1 件 |

取得した補正 JSON は通常の分析結果と同じスキーマで正規化する。
正規化できない場合は完全一致結果なしとして扱う。

完全一致結果を利用する場合、監査項目は次の通り設定する。

| 項目 | 値 |
|---|---|
| prompt version | 通常の prompt version に `-exact-feedback` を付与 |
| prompt hash | 空文字 |
| retrieved rag cases | case id、similarity 100、label、reason tag、match `exact` |

## 9. Ollama リクエスト

HTTP はブロッキング API のため `asyncio.to_thread` で実行し、同時実行数は `OLLAMA_MAX_CONCURRENCY` の semaphore で制限する。
URL 文脈取得も別 semaphore で制限し、同時取得数は `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CONCURRENCY` 以上 1 とする。

リクエスト前に、同一 guild の管理者確認済みフィードバックから類似事例を取得し、対象メッセージ内 URL からリンク先文脈を作成する。取得後、リクエスト payload は以下とする。

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
| last user message | user prompt template に context、target、URL 文脈、投稿者文脈を埋め込んだ文字列 |

対象本文は `OLLAMA_MESSAGE_MAX_CHARS` で後方切り詰める。
文脈は `OLLAMA_CONTEXT_MAX_CHARS` で後方切り詰める。
URL 文脈は `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CHARS` で後方切り詰める。
user prompt template に `{url_context_text}` がない場合は、末尾に URL 文脈用の段落を追加してから format する。
user prompt template に `{target_author_text}` がない場合は、末尾に投稿者文脈用の段落を追加してから format する。
template format に失敗した場合は既定 template で format する。

## 10. Ollama 再試行

Ollama 応答が次のいずれかに該当する場合、再試行対象とする。

| 条件 | 内容 |
|---|---|
| length limit | `done_reason` が length |
| empty content | assistant content が空 |
| invalid JSON | JSON parse または最初の JSON object 抽出に失敗 |

再試行は次の順序で行う。

| 順序 | 内容 |
|---:|---|
| 1 | 通常 prompt、通常文脈長、`OLLAMA_NUM_PREDICT` で実行する |
| 2 | 文脈と URL 文脈を `OLLAMA_RETRY_CONTEXT_MAX_CHARS` に縮小し、出力上限を通常値の 2 倍以上へ増やして実行する |
| 3 | 対象本文のみを最大 500 文字に縮小し、投稿者文脈と既定 system prompt と最小 user prompt で実行する |

通常の `OLLAMA_NUM_PREDICT` が 0 以下の場合、再試行でもその特殊値を維持する。
最小 prompt 再試行では出力上限を 512 以上 1024 以下の範囲に収める。
最小 prompt 再試行の結果には、prompt version に `-minimal-retry` を付与し、参照 RAG 事例は空配列とする。

## 11. URL 文脈取得

URL 文脈取得が無効な場合は `(URL context disabled)` を返す。
対象本文に URL がない場合、または安全に取得できた本文がない場合は `(no safely fetched linked pages)` を返す。

URL 抽出は HTTP/HTTPS URL のみを対象とし、末尾の句読点や括弧類を除去する。
同一 URL は 1 回だけ扱い、取得件数は `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_URLS` までとする。

URL 安全確認は取得前、リダイレクト時、最終 URL に対して行う。

| 項目 | 条件 |
|---|---|
| scheme | `http` または `https` |
| userinfo | username/password を含まない |
| host | 空でない |
| port | 未指定、80、443 のいずれか |
| localhost | `localhost` と `localhost.localdomain` は拒否 |
| 名前解決 | hostname の解決結果が 1 件以上ある |
| IP address | global address かつ multicast でない |

取得リクエストでは専用 User-Agent を設定し、HTML、plain text、XHTML を優先する Accept header を送信する。
timeout は `OLLAMA_ANALYSIS_URL_CONTEXT_TIMEOUT_SECONDS`、読み込み上限は `OLLAMA_ANALYSIS_URL_CONTEXT_MAX_BYTES` とする。
上限を超える応答は本文抽出せず skip 理由を URL 文脈へ記録する。

content type は `text/html`、`text/plain`、`application/xhtml+xml`、未指定のみ対応する。
charset が指定されていればそれを使い、未指定なら UTF-8 として decode する。
HTML は script、style、noscript、template、svg を除去し、title、meta description、body text を抽出する。
plain text はそのまま本文候補とする。
抽出後は連続空白を 1 つに圧縮する。

prompt に渡す URL 文脈には、リンク先本文は投稿者本人の直接発話ではなく、対象メッセージの参照先理解にのみ使う旨を含める。
各 URL は、取得成功なら最終 URL、content type、本文抜粋を含める。
取得失敗または拒否なら URL と skip 理由を含める。

## 12. few-shot

few-shot JSON は配列のみ有効とする。
各要素は `input` または `message`、`output` または `judgment` を持つ dict とする。
最大件数は `OLLAMA_ANALYSIS_FEWSHOT_MAX_EXAMPLES`。output は通常結果と同じ正規化を通す。
few-shot file が存在しない、JSON として読めない、または配列でない場合は空配列として扱う。

## 13. フィードバック RAG

RAG が無効、guild id がない、候補数または最大採用数が 0 以下の場合は空配列を返す。

候補は同一 guild の確認済みフィードバックから取得する。
条件は `review_status=CONFIRMED`、`corrected_result_json` が空でないこと。
対応する message content が空でない行を、作成日時と id の降順で取得する。
取得上限は候補数、検索 pool 数、最大採用数の最大値とする。

対象検索文は、対象メッセージ、直前会話の末尾 5 件、対象メッセージが 12 文字以下の場合の `補足: 短文` で構成する。候補検索文は、過去の対象メッセージ、管理者判断 label、理由タグ、note で構成する。
URL、Discord mention、channel mention、長い数字列、ゼロ幅文字は検索用に正規化する。

類似度は次の軽量特徴で算出する。

1. 英数字と日本語連続文字を token 化する。
2. 空白を除去した文字列から 2-gram と 3-gram を追加する。
3. 3 文字以下の短文では 1 文字 token も追加する。
4. 左右 token の積集合数を、左右 token 数の小さい方で割り、100 倍して四捨五入する。

embedding RAG が有効で、候補に embedding JSON が存在する場合は、対象検索文の embedding を取得する。
候補 embedding は現在の embedding model と一致する場合だけ使用する。
cosine similarity を 0 から 100 に丸め、`OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_MIN_SIMILARITY` 未満なら 0 とする。

類似度が `OLLAMA_ANALYSIS_FEEDBACK_RAG_MIN_SIMILARITY` 未満の候補は除外する。
補正 JSON を正規化できない候補も除外する。
残った候補を類似度降順に並べ、最大 `OLLAMA_ANALYSIS_FEEDBACK_RAG_MAX_EXAMPLES` 件採用する。

最終類似度は次の値の最大値とする。

| 要素 | 補正 |
|---|---|
| 対象本文同士の語彙類似度 | そのまま |
| 対象検索文と候補検索文の語彙類似度 | 0.85 倍 |
| 対象本文と管理者 note の語彙類似度 | 0.75 倍 |
| embedding 類似度 | しきい値以上の場合のみ採用 |

本文が完全一致する場合は 100、片方がもう片方を含む場合は最低 88 とする。
対象本文が 12 文字以下で本文類似度が 60 以上なら 15 加点し、上限は 100 とする。
label が `false_positive`、`false_negative`、`unsure` で note 類似度が 45 以上なら 10 加点する。

採用例は prompt に次の形で追加する。

| role | content |
|---|---|
| user | 管理者確認済みの動的参考事例を使うが、機械的にコピーしない旨の説明 |
| user | 例番号、類似度、label、理由タグに基づく context、対象メッセージ、note、過去分析スコア |
| assistant | 補正済み結果 JSON |

## 14. RAG 過検出ガード

通常分析とミーム曖昧性ガードの後、採用済み RAG 事例の中に安全に再利用できる `false_positive` 事例があれば、決定的な後処理でスコアを丸める。

適用条件は次の通り。

| 項目 | 条件 |
|---|---|
| 明示的な実害 signal | 含まない |
| label | `false_positive` |
| 類似度 | `82` 以上 |
| 補正結果 targeted | false |
| 補正結果 max score | `40` 以下 |

適用時は 6 スコアを、補正結果の最大スコア + 10 と `40` の小さい方以下に丸める。
targeted は false、context dependency は true とする。
confidence は `70` 以下に丸める。
raw result には `rag_feedback_guard_applied=true`、参照 case id、理由タグを含める。
reason には高類似の `false_positive` 事例による補正である旨を追記する。

## 15. フィードバック embedding

管理者フィードバック登録時、補正結果があり対象メッセージ本文を取得できる場合は embedding 列を作成できる。
ただし通常は `OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_RAG_ENABLED` が true の場合のみ作成する。
バックフィル処理では force 指定により embedding RAG 無効時も作成する。

embedding 入力文字列は次の要素を改行連結する。

| 順序 | 内容 |
|---:|---|
| 1 | `target:` |
| 2 | 正規化した対象本文 |
| 3 | `label:` |
| 4 | 管理者 label |
| 5 | `reason_tag:` |
| 6 | 理由タグ |
| 7 | note がある場合は `note:` と正規化 note |

embedding API へは model と prompt を JSON で送信する。
応答は `embedding`、または `embeddings` の先頭要素から取得し、float 配列へ変換する。
保存項目は embedding model、embedding text hash、embedding dimension、embedding JSON とする。

embedding text hash は embedding 入力文字列の UTF-8 SHA-256 hex digest とする。
embedding JSON は余分な空白を含まない JSON 配列として保存する。

## 16. ミーム曖昧性ガード

通常分析結果が返った後、設定が有効なら対象本文にミームらしさがあるか判定する。
ミームらしさがない場合、または明示的な実害 signal がある場合は結果を変更しない。
targeted が true、confidence が 80 以上、context dependency が false の場合も結果を変更しない。

ミームらしさは次のいずれかで判定する。

| 条件 | 内容 |
|---|---|
| 笑い表現 | `w` の連続、`ｗ` の連続、`草`、`笑`、笑い emoji |
| 日本語末尾 `w` | 日本語を含む正規化文字列が `w` で終わる |
| 定型語 | ネタ、ミーム、構文、コピペ、定期、元ネタ、消す方法などの marker を含む |

明示的な実害 signal は、Discord user mention、または殺害、暴行、晒し、特定、襲撃、脅迫系の語を含む場合とする。

ガード適用時は 6 スコアすべてを `OLLAMA_ANALYSIS_MEME_GUARD_SCORE_CAP` 以下に丸める。
confidence は `OLLAMA_ANALYSIS_MEME_GUARD_CONFIDENCE_CAP` 以下に丸める。
context dependency は true にし、reason が空なら `ミーム文脈不明` を設定する。
raw result には `meme_guard_applied=true` を含める。

## 17. JSON 解析

Ollama の assistant content を取得する。
空の場合は done reason または error を含む `ValueError` とする。
content が Markdown code fence の場合は fence を除去する。
通常 JSON parse に失敗した場合は、最初の balanced JSON object を抽出して再 parse する。

## 18. 結果正規化

| 項目 | 正規化 |
|---|---|
| aggression/intimidation/insult/sarcasm/snide/discomfort | int 化し 0 から 100 に clamp |
| targeted | bool、既定 true |
| confidence | int 化し 0 から 100 に clamp |
| context_dependency | bool、既定 false |
| reason | strip 済み文字列 |

bool は bool、数値、`true/1/yes/y/on`、`false/0/no/n/off` を解釈する。

## 19. 判定

`max_score` は 6 スコアすべての最大値。通知判定用スコアは aggression、intimidation、insult、discomfort の最大値。

| 判定 | 条件 |
|---|---|
| should_react | 通知判定用スコアが `OLLAMA_REACTION_THRESHOLD` 以上 |
| should_notify | 通知判定用スコアが `OLLAMA_DM_THRESHOLD` 以上 |

ただし confidence が `OLLAMA_CONFIDENCE_THRESHOLD` 未満なら false。
targeted が true なら alert 可。
targeted が false の場合は intimidation が 80 以上のときのみ alert 可。

## 20. 保存

分析結果は message id 単位で insert ignore する。
保存項目は message/guild/channel/user/model、6 スコア、max score、targeted、confidence とする。
context dependency、reason、raw result JSON、prompt version、prompt hash も保存する。
参照 RAG 事例 JSON、should_react、should_notify も保存する。

prompt version は `OLLAMA_ANALYSIS_PROMPT_VERSION` を使用する。
prompt hash は Ollama に送信する messages を key sort 付き JSON にする。
その UTF-8 bytes の SHA-256 hex digest とする。
参照 RAG 事例は case id、similarity、label、reason tag の配列として保存する。
完全一致フィードバックを利用した場合は prompt hash を空文字とし、参照 RAG 事例に `match=exact` を含める。
最小 prompt 再試行を利用した場合は参照 RAG 事例を空配列とする。

保存済み message の再分析では Bot 投稿、空 content、`!` 始まりを無視し、リアクションと DM は行わない。

## 21. 通知

should_react が true の場合、対象 message に `✖` リアクションを追加する。
失敗はログ出力のみ。
さらに通知チャンネル id が設定されている場合、Bot cache または fetch で channel を取得する。
guild id 設定がある場合は channel guild と一致するか確認して送信する。

should_notify が true の場合、投稿者へ日本語 DM を送信する。DM 失敗はログ出力のみ。

## 22. フィードバック

`analysis feedback <message_id> <label> [reason_tag] [note]` は guild 限定、管理者のみ。
message id は decimal 文字列のみ受け付ける。
保存済み message が別 guild の場合はエラーにする。

label alias は次の通り。

| 入力 | 保存値 |
|---|---|
| `ok`、`correct`、`true`、`正しい` | `correct` |
| `fp`、`false_positive`、`誤検知` | `false_positive` |
| `fn`、`false_negative`、`見逃し` | `false_negative` |
| `unsure`、`unknown`、`不明` | `unsure` |

reason tag alias は次の通り。

| 入力例 | 保存値 |
|---|---|
| 空、`none`、`no_tag`、`unspecified`、`未指定` | `unspecified` |
| `meme`、`ミーム`、`ネタ` | `meme` |
| `inside_joke`、`inner_joke`、`内輪ネタ` | `inside_joke` |
| `game`、`game_context`、`ゲーム` | `game_context` |
| `external_news`、`external_news_comment`、`news`、`外部ニュース`、`url` | `external_news_comment` |
| `external_criticism`、`criticism`、`批判`、`非難` | `external_criticism` |
| `sexual`、`sexual_banter`、`猥談` | `sexual_banter` |
| `roleplay`、`rp`、`ロールプレイ` | `roleplay` |
| `quote`、`quotation`、`引用` | `quote` |
| `direct_attack`、`attack`、`直接攻撃` | `direct_attack` |
| `intimidation`、`threat`、`威圧`、`脅迫` | `intimidation` |

slash command では label と reason tag を日本語補足付きの選択肢として表示する。
prefix command では reason tag として正規化できない第 3 引数を note の一部として扱い、旧構文との互換性を維持する。

フィードバック登録時は、対象 message が別 guild に属していればエラーにする。既存分析結果がある場合は message id で取得する。

補正結果は次の優先順で作成する。

1. note に JSON object が含まれる場合、最初の balanced JSON object を抽出して分析結果スキーマで正規化する。
2. label が `correct` で既存分析結果がある場合、既存分析結果を補正結果として保存する。
3. label が `false_positive` の場合、6 スコアを低くした過検出補正結果を保存する。
4. 上記以外は補正結果なしとする。

補正結果がある場合は `review_status=CONFIRMED` とする。
補正結果がない場合は `review_status=PENDING` とする。
保存項目は message/guild/channel/user/reviewer、label、reason tag、review status、corrected result JSON、note とする。
補正結果と対象本文がある場合は、embedding model、embedding text hash、embedding dimension、embedding JSON も保存する。

## 23. ホワイトリスト

`analysis whitelist` は guild 限定、管理者のみ。
分析除外ルールは guild 単位で管理し、有効なルールだけを通常の分析対象判定で使用する。

| コマンド | 処理 |
|---|---|
| `analysis whitelist add <rule_type> <pattern>` | ルール種別と照合値を正規化し、有効状態で追加する |
| `analysis whitelist list [all]` | 有効ルールを id 昇順で最大 30 件表示する。`all` 指定時は無効ルールも含める |
| `analysis whitelist enable <id>` | 同一 guild の指定ルールを有効化する |
| `analysis whitelist disable <id>` | 同一 guild の指定ルールを無効化する |

ルール種別は次の通り。

| rule_type | 照合 |
|---|---|
| `text_exact` | 空白を正規化した本文が pattern と完全一致する |
| `text_contains` | 空白を正規化した本文に pattern が含まれる |
| `user` | 投稿者 user id が pattern の Discord ID と一致する |
| `channel` | 投稿 channel id が pattern の Discord ID と一致する |

`user` と `channel` の pattern は Discord ID 文字列のみ受け付ける。
本文系 pattern は前後空白を除去し、空文字はエラーにする。
一致判定用の本文は改行を含む連続空白を 1 文字の空白へ正規化する。

## 24. 評価と embedding バックフィル

確認済みフィードバックを評価データとして、現在の分析結果と補正結果を比較できる。
評価時は完全一致フィードバック再利用を無効化し、現在評価中の message id を RAG 候補から除外する。

評価対象は `CONFIRMED`、補正 JSON あり、対象メッセージ本文ありの行とする。
guild id 指定がある場合は同一 guild のみ対象にする。

評価指標は次の通り。

| 指標 | 内容 |
|---|---|
| alert accuracy | 期待結果と実結果の should react が一致した割合 |
| targeted accuracy | targeted が一致した割合 |
| score MAE | 6 スコアの平均絶対誤差 |
| max score error | 最大スコアの絶対誤差 |
| rag feedback guard applied | RAG 過検出ガードが適用された件数 |

dry run では対象 case だけを表示し、Ollama 分析は行わない。
URL 文脈は評価 option で有効化された場合だけ取得する。
評価サマリは label 別、reason tag 別の case/analyzed/failed 件数も保持する。

embedding バックフィルは、確認済みフィードバックのうち embedding 未作成の行を id 降順で処理する。
limit が 0 の場合は対象がなくなるまで処理する。
force 指定時は既存 embedding も再作成する。
dry run では候補表示のみを行い、Ollama embedding API と DB 更新は行わない。
