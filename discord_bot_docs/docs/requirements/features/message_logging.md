# メッセージログ要件

## 1. 概要

Discord サーバー内のメッセージ投稿、編集、削除を記録し、監査や分析に利用できる状態で保持する。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-LOG-001 | 投稿されたメッセージを保存できること。 |
| FR-LOG-002 | メッセージ編集時に編集前後の内容を保存できること。 |
| FR-LOG-003 | メッセージ削除時に削除対象の内容を保存できること。 |
| FR-LOG-004 | 添付、埋め込み、スタンプ、固定状態など、確認に必要な付帯情報を保存できること。 |
| FR-LOG-005 | 管理者は既存メッセージ履歴を指定件数で取り込めること。 |
| FR-LOG-006 | Bot 自身の投稿や保存対象外のメッセージは、必要に応じて除外できること。 |

## 3. 入出力

| 区分 | 内容 |
|---|---|
| 入力 | Discord のメッセージ作成・編集・削除イベント、バックフィルコマンド |
| 出力 | メッセージログ、編集ログ、削除ログ |

## 4. 関連文書

- [メッセージログ設計](../../basic_design/features/message_logging.md)
- [メッセージログ詳細](../../detailed_design/features/message_logging.md)
- [message_log](../../table_definitions/tables/message_log.md)
- [message_edit_log](../../table_definitions/tables/message_edit_log.md)
- [message_delete_log](../../table_definitions/tables/message_delete_log.md)
