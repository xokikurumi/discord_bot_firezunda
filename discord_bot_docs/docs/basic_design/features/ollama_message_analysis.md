# Ollama メッセージ分析設計

## 概要

投稿メッセージを Ollama API へ送信し、攻撃性、威圧、侮辱、皮肉、嫌味、不快可能性などの分析結果を保存する。管理者フィードバックを蓄積し、類似する確認済み事例を動的 few-shot として分析プロンプトに加える。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `MessageWatcherCog` |
| Service | `MessageWatcherService` |
| Repository | `MessageAnalysisLogRepository`, `MessageAnalysisFeedbackRepository`, `MessageLogRepository` |
| テーブル | `message_analysis_log`, `message_analysis_feedback`, `message_log` |

## 処理

| 処理 | 内容 |
|---|---|
| 文脈取得 | 対象メッセージ周辺の過去メッセージを取得する。 |
| フィードバック事例取得 | 管理者確認済みフィードバックから、対象メッセージと類似する補正事例を取得する。 |
| 分析要求 | Ollama Chat API へ分析プロンプトを送信する。 |
| 正規化 | JSON 応答をパースし、スコアと理由を正規化する。 |
| 保存 | 分析結果、raw result、prompt version、prompt hash、参照事例を保存する。 |
| 通知 | しきい値に応じてリアクションまたは DM 通知を行う。 |
| フィードバック | 管理者が判定妥当性と補正結果を登録し、以降の分析精度向上に利用する。 |

## フィードバック RAG

| 項目 | 内容 |
|---|---|
| 対象 | 同一 guild の `CONFIRMED` かつ補正 JSON を持つフィードバック |
| 候補数 | 設定値で上限を制御する |
| 類似度 | 対象メッセージ、直前会話、管理者判断、補足を軽量な語彙特徴で比較する |
| 採用条件 | 類似度が設定された最小値以上であること |
| prompt 利用 | 管理者確認済みの動的 few-shot として user/assistant message を追加する |
| 監査 | 採用した case id、類似度、label を分析結果に保存する |
