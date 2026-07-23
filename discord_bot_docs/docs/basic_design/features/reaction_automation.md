# リアクション自動化設計

## 概要

登録キーワードに一致したメッセージへ自動でリアクションを付与する。NG ワード設定によりリアクション抑止も行う。

## 構成

| 項目 | 内容 |
|---|---|
| Cog | `MessageReactionCog` |
| Service | `MessageReactionService` |
| Repository | `ReactionKeyworkdsRepository` |
| テーブル | `b_reaction_keywords` |

## コマンド

| コマンド | 内容 |
|---|---|
| `reaction add` | キーワードとリアクションを登録する。 |
| `reaction remove` | キーワード設定を削除する。 |
| `reaction list` | 登録済み設定を表示する。 |
| `reaction check_emoji` | 絵文字利用可否を確認する。 |

## イベント

| 種別 | 名前 | 内容 |
|---|---|---|
| Event | `on_message` | メッセージ本文を正規化し、登録キーワードと照合する。 |
