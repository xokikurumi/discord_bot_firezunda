# Ollama メッセージ分析要件

## 1. 概要

メッセージを Ollama へ送信して内容を分析し、分析結果を保存し、必要に応じてリアクションまたは通知を行う。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-AI-001 | メッセージ本文を分析対象として Ollama に送信できること。 |
| FR-AI-002 | 攻撃性、威圧、侮辱、皮肉、嫌味、不快可能性などの分析結果を保存できること。 |
| FR-AI-003 | しきい値を超えた場合、リアクション付与または DM 通知を実行できること。 |
| FR-AI-004 | 同一メッセージの分析結果を重複保存しないこと。 |
| FR-AI-005 | 分析対象外のメッセージを除外できること。 |
| FR-AI-006 | Ollama 連携に失敗してもメッセージ処理全体を停止しないこと。 |
| FR-AI-007 | 管理者は分析結果に対して正解、過検出、見逃し、不明のフィードバックを登録できること。 |
| FR-AI-008 | 管理者が確認済みのフィードバックを、類似メッセージ分析時の動的な参考事例として利用できること。 |
| FR-AI-009 | 分析結果にはプロンプトバージョン、プロンプトハッシュ、参照したフィードバック事例を監査用に保存できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | Discord メッセージ、分析設定、管理者フィードバック |
| 出力 | 分析結果、リアクション、DM 通知、フィードバック履歴 |

## 4. 関連文書

- [Ollama メッセージ分析設計](../../basic_design/features/ollama_message_analysis.md)
- [Ollama メッセージ分析詳細](../../detailed_design/features/ollama_message_analysis.md)
- [Ollama メッセージ分析バッチ](../../batch_definitions/batches/ollama_message_analysis.md)
- [message_analysis_log](../../table_definitions/tables/message_analysis_log.md)
- [message_analysis_feedback](../../table_definitions/tables/message_analysis_feedback.md)
