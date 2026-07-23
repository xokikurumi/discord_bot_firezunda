# コミュニケーション傾向分析設計

## 概要

半期ごとのメッセージ活動を集計し、Ollama による傾向分析レポートを保存する。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `CommunicationTrendCog` |
| Service | `CommunicationTrendService` |
| Repository | `CommunicationTrendAnalysisRepository` |
| テーブル | `communication_trend_analysis`, `message_log`, `message_edit_log`, `message_delete_log`, `message_analysis_log` |

## 実行条件

| 種別 | 条件 |
|---|---|
| 定期実行 | JST の 1 月 1 日、6 月 1 日に実行する。 |
| 手動実行 | 管理者が `communication_trend_analyze` を実行する。 |

## 分析単位

| 単位 | 内容 |
|---|---|
| user | ギルド内のユーザー単位で分析する。 |
| guild | 設定が有効な場合、ギルド全体を分析する。 |
