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
| FR-AI-010 | 管理者確認済みフィードバックと本文が完全一致する場合、同じ補正結果を優先利用できること。 |
| FR-AI-011 | メッセージ内 URL のリンク先本文を、安全に取得できる範囲で分析文脈へ追加できること。 |
| FR-AI-012 | URL 文脈取得では、許可された scheme、port、公開 IP、content type、サイズ上限を満たさない取得を抑止できること。 |
| FR-AI-013 | Ollama 応答が長さ制限や不正 JSON で失敗した場合、文脈を縮小した再試行と最小プロンプト再試行を行えること。 |
| FR-AI-014 | 管理者は guild 単位で本文完全一致、本文部分一致、ユーザー、チャンネルの分析除外ルールを管理できること。 |
| FR-AI-015 | 固定 few-shot と system prompt をファイルまたは環境変数から差し替えられること。 |
| FR-AI-016 | 管理者フィードバックは語彙類似度に加え、任意で embedding 類似度により検索できること。 |
| FR-AI-017 | ミーム、定型ネタ、内輪文脈が疑われる曖昧な投稿は、明示的な実害 signal がない限り過検出を抑止できること。 |
| FR-AI-018 | 確認済みフィードバックを評価データとして、現在の解析挙動を検証できること。 |
| FR-AI-019 | 管理者フィードバックには、過検出や見逃しの理由を分類する理由タグを登録できること。 |
| FR-AI-020 | 高類似の過検出フィードバックを参照した場合、補正済み結果が低リスクであれば決定的な後処理で再過検出を抑止できること。 |
| FR-AI-021 | 分析時は対象投稿者の guild 内表示名、global 名、ユーザー名を補助文脈として利用できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | Discord メッセージ、分析設定、管理者フィードバック、理由タグ、分析除外ルール |
| 出力 | 分析結果、リアクション、DM 通知、フィードバック履歴、分析除外ルール |

## 4. 関連文書

- [Ollama メッセージ分析設計](../../basic_design/features/ollama_message_analysis.md)
- [Ollama メッセージ分析詳細](../../detailed_design/features/ollama_message_analysis.md)
- [Ollama メッセージ分析バッチ](../../batch_definitions/batches/ollama_message_analysis.md)
- [message_analysis_log](../../table_definitions/tables/message_analysis_log.md)
- [message_analysis_feedback](../../table_definitions/tables/message_analysis_feedback.md)
- [message_analysis_whitelist](../../table_definitions/tables/message_analysis_whitelist.md)
