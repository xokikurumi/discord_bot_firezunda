# Niconico Info 通知要件

## 1. 概要

Niconico Info と niconews の記事を確認し、条件に一致する未通知記事を Discord へ通知する。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-NICO-INFO-001 | Niconico Info または niconews のカテゴリページから通知対象記事を検出できること。 |
| FR-NICO-INFO-002 | 検出記事を保存できること。 |
| FR-NICO-INFO-003 | 未通知記事を通知し、通知済み状態を保存できること。 |
| FR-NICO-INFO-004 | include / exclude のキーワードフィルタを管理できること。 |
| FR-NICO-INFO-005 | 記事概要を通知本文に含められること。 |
| FR-NICO-INFO-006 | 定期確認と手動確認の両方で記事確認を実行できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | 記事ページ、フィルタ設定、通知設定 |
| 出力 | 記事情報、通知済み状態、Discord 通知 |

## 4. 関連文書

- [Niconico Info 通知設計](../../basic_design/features/niconico_info.md)
- [Niconico Info 通知詳細](../../detailed_design/features/niconico_info.md)
- [Niconico Info 確認・通知](../../batch_definitions/batches/niconico_info_check.md)
- [niconico_info_event](../../table_definitions/tables/niconico_info_event.md)
- [niconico_info_filter](../../table_definitions/tables/niconico_info_filter.md)
