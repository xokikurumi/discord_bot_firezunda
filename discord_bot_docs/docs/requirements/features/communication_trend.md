# コミュニケーション傾向分析要件

## 1. 概要

半期単位でメッセージ、編集、削除、分析ログを集計し、ユーザーまたはギルド単位の傾向を保存する。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-TREND-001 | 半期ごとにメッセージ関連ログを集計できること。 |
| FR-TREND-002 | ユーザー単位の傾向分析結果を保存できること。 |
| FR-TREND-003 | ギルド単位の傾向分析結果を保存できること。 |
| FR-TREND-004 | 管理者は手動分析を実行できること。 |
| FR-TREND-005 | 分析結果は Discord へ自動投稿せず、内部保存できること。 |
| FR-TREND-006 | 対象期間、投稿数、編集数、削除数、分析指標を保存できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | メッセージログ、編集ログ、削除ログ、分析ログ |
| 出力 | コミュニケーション傾向分析結果 |

## 4. 関連文書

- [コミュニケーション傾向分析設計](../../basic_design/features/communication_trend.md)
- [コミュニケーション傾向分析詳細](../../detailed_design/features/communication_trend.md)
- [コミュニケーション傾向分析バッチ](../../batch_definitions/batches/communication_trend_analysis.md)
- [communication_trend_analysis](../../table_definitions/tables/communication_trend_analysis.md)
