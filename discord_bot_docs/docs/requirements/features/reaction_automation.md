# リアクション自動化要件

## 1. 概要

メッセージ内容に応じてリアクションを自動付与し、管理者がキーワードと絵文字の対応を管理できるようにする。

## 2. 機能要求

| ID | 要件 |
|---|---|
| FR-REACTION-001 | 管理者はキーワードとリアクションの組み合わせを登録できること。 |
| FR-REACTION-002 | 管理者は登録済みキーワードを削除できること。 |
| FR-REACTION-003 | 利用者は登録済みキーワードの一覧を確認できること。 |
| FR-REACTION-004 | メッセージ本文が登録キーワードに一致した場合、対応するリアクションを付与できること。 |
| FR-REACTION-005 | NG 条件に一致した場合、通常リアクションを抑止できること。 |
| FR-REACTION-006 | 管理者は Bot が利用可能な絵文字か確認できること。 |
| FR-REACTION-007 | 初期リアクション設定を必要に応じて投入できること。 |

## 3. 権限

| 操作 | 権限 |
|---|---|
| 登録・削除・初期投入 | 管理者 |
| 一覧・絵文字確認 | サーバー内利用者 |

## 4. 関連文書

- [リアクション自動化設計](../../basic_design/features/reaction_automation.md)
- [リアクション自動化詳細](../../detailed_design/features/reaction_automation.md)
- [b_reaction_keywords](../../table_definitions/tables/b_reaction_keywords.md)
