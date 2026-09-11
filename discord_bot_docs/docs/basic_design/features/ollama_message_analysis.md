# Ollama メッセージ分析設計

## 概要

投稿メッセージを Ollama API へ送信し、攻撃性、威圧、侮辱、皮肉、嫌味、不快可能性などの分析結果を保存する。管理者フィードバックを蓄積し、本文完全一致または類似する確認済み事例を分析に利用する。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `MessageWatcherCog`, `AnalysisCog` |
| Service | `MessageWatcherService` |
| Repository | `MessageAnalysisLogRepository`, `MessageAnalysisFeedbackRepository`, `MessageAnalysisWhitelistRepository`, `MessageLogRepository` |
| テーブル | `message_analysis_log`, `message_analysis_feedback`, `message_analysis_whitelist`, `message_log` |

## 処理

| 処理 | 内容 |
|---|---|
| 文脈取得 | 対象メッセージ周辺の過去メッセージを取得する。 |
| 投稿者文脈取得 | 対象投稿者の guild 表示名、global 名、ユーザー名を取得し、本文ではなく補助文脈として扱う。 |
| 完全一致フィードバック取得 | 同一 guild の確認済みフィードバックから、対象本文と完全一致する補正結果を取得する。 |
| フィードバック事例取得 | 管理者確認済みフィードバックから、対象メッセージと類似する補正事例を取得する。 |
| URL 文脈取得 | 対象メッセージ内 URL から、安全に取得できるリンク先本文抜粋を作成する。 |
| 分析要求 | Ollama Chat API へ分析プロンプトを送信する。 |
| 再試行 | 応答が長さ制限や不正 JSON で解析不能な場合、文脈を縮小して再試行し、最後に最小プロンプトで再試行する。 |
| ミーム曖昧性ガード | ミームや定型ネタの可能性が高く実害 signal がない場合、スコアと信頼度を上限値以下に抑える。 |
| RAG 過検出ガード | 高類似の `false_positive` 事例が低リスク補正済みであれば、通常分析後にスコアと信頼度を安全側へ丸める。 |
| 正規化 | JSON 応答をパースし、スコアと理由を正規化する。 |
| 保存 | 分析結果、raw result、prompt version、prompt hash、参照事例を保存する。 |
| 通知 | しきい値に応じてリアクションまたは DM 通知を行う。 |
| フィードバック | 管理者が判定妥当性と補正結果を登録し、以降の分析精度向上に利用する。 |
| ホワイトリスト | 管理者が登録した除外ルールに一致するメッセージを分析対象外にする。 |
| 評価 | 確認済みフィードバックを使い、現在の解析結果と補正結果を比較する。 |

## ホワイトリスト

| 項目 | 内容 |
|---|---|
| 管理単位 | guild 単位 |
| ルール種別 | 本文完全一致、本文部分一致、ユーザーID、チャンネルID |
| 管理操作 | 追加、一覧、有効化、無効化 |
| 評価位置 | 機能有効、本文あり、コマンド風メッセージ除外の後、Ollama 分析より前 |
| 一致時処理 | 分析結果を保存せず、リアクションや通知も行わない |

## 完全一致フィードバック

| 項目 | 内容 |
|---|---|
| 対象 | 同一 guild の `CONFIRMED` かつ補正 JSON を持つフィードバック |
| 照合 | 保存済みメッセージ本文を trim し、対象本文と完全一致させる |
| 優先度 | Ollama 分析、URL 文脈取得、類似 RAG より先に評価する |
| 結果 | 補正 JSON を正規化し、同じ判定結果として返す |
| 監査 | `exact-feedback` 系の prompt version と、similarity 100 の参照事例を保存する |

## フィードバック RAG

| 項目 | 内容 |
|---|---|
| 対象 | 同一 guild の `CONFIRMED` かつ補正 JSON を持つフィードバック |
| 候補数 | 設定値で上限を制御する |
| 類似度 | 対象メッセージ、直前会話、管理者判断、補足を軽量な語彙特徴で比較する |
| embedding | 設定有効時は保存済み embedding と対象検索文 embedding の cosine 類似度も利用する |
| 採用条件 | 類似度が設定された最小値以上であること |
| prompt 利用 | 管理者確認済みの動的 few-shot として user/assistant message を追加する |
| 監査 | 採用した case id、類似度、label、理由タグを分析結果に保存する |

## フィードバック理由タグ

| 項目 | 内容 |
|---|---|
| 保存値 | `unspecified`、`meme`、`inside_joke`、`game_context`、`external_news_comment`、`external_criticism`、`sexual_banter`、`roleplay`、`quote`、`direct_attack`、`intimidation` |
| 表示 | slash command では日本語補足付きの選択肢として表示する |
| prefix 互換 | reason tag として解釈できない第 3 引数は従来の note として扱う |
| 利用箇所 | RAG prompt、embedding 入力、評価サマリ、RAG 過検出ガードの監査項目 |

## URL 文脈

| 項目 | 内容 |
|---|---|
| 対象 URL | メッセージ本文内の HTTP/HTTPS URL |
| 件数上限 | 設定値で取得対象 URL 数を制御する |
| 安全確認 | scheme、userinfo、host、port、名前解決結果、redirect 先を検証する |
| 取得制限 | timeout、最大 byte 数、最大 prompt 文字数を設定値で制御する |
| content type | HTML、plain text、XHTML のみ本文抽出対象とする |
| prompt 利用 | リンク先本文は発言者本人の発話ではなく参照文脈として扱うよう明示する |

## ミーム曖昧性ガード

| 項目 | 内容 |
|---|---|
| 対象 | 笑い表現、ミーム marker、定型ネタらしさを含む投稿 |
| 除外 | Discord user mention や明示的な脅迫・晒し等の実害 signal がある投稿 |
| 抑止内容 | 攻撃性など 6 スコアと confidence を設定上限以下に丸める |
| 文脈扱い | 抑止時は context dependency を true にする |
