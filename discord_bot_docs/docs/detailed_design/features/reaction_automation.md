# リアクション自動化詳細

## 1. 目的

guild ごとにキーワードとリアクションを登録し、ユーザー投稿に一致した場合に自動リアクションを付与する。NG キーワードに一致した場合は通常リアクションを抑止する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| MessageReactionCog | `reaction` コマンド群と投稿 listener を提供する |
| MessageReactionService | キーワード登録、正規化、絵文字解析、リアクション付与を行う |
| ReactionKeyworkdsRepository | キーワード行の insert、soft delete、一覧、反応対象取得を行う |

## 3. コマンド

| コマンド | 権限 | 処理 |
|---|---|---|
| `reaction` | guild | usage を表示 |
| `reaction add <keyword> <reaction> [ng_word]` | 管理者 | キーワードを追加 |
| `reaction remove <keyword>` | 管理者 | キーワードを soft delete |
| `reaction list` | guild | キーワード一覧を表示 |
| `reaction check_emoji <emoji>` | guild | カスタム絵文字可視性と権限を診断 |
| `reaction seed_syukka` | 管理者 | 既定プリセットを追加 |

## 4. テキスト正規化

キーワード照合前に、対象文字列と登録キーワードの両方を正規化する。

1. null は空文字にする。
2. Unicode NFKC 正規化を行う。
3. カタカナを対応するひらがなへ変換する。
4. 長音記号を削除する。
5. 同一文字の連続を 1 文字に畳む。
6. casefold する。

## 5. bool 解析

`ng_word` は bool の場合そのまま返し、文字列の場合 `1`、`true`、`yes`、`y`、`on`、`ng` を true とする。それ以外は false。

## 6. リアクション解析

カスタム絵文字 mention `<:name:id>` または `<a:name:id>` は、name、id、animation flag に分解する。
該当しない場合は Unicode emoji として `reaction` にそのまま保存する。
id は null、animation は false とする。

## 7. 登録処理

`reaction add` は解析結果を使用し、guild id、enabled、keyword、reaction を保存する。
reaction id、animation flag、ng word flag、delete flag も保存する。
カスタム絵文字 id が Bot cache に存在しない場合は警告文を追加して応答する。

## 8. 削除処理

`reaction remove` は物理削除せず、guild id と keyword で対象を soft delete する。更新件数が 0 の場合は未検出メッセージを返す。

## 9. 一覧処理

削除されていない guild キーワードを取得する。カスタム絵文字は `<a:name:id>` または `<:name:id>` に再構築する。1900 文字を超える前に分割送信する。

## 10. プリセット

`seed_syukka` は次のルールを登録する。正規化済み keyword と ng flag の組み合わせが既存の場合は skip する。

| keyword | reaction | ng_word |
|---|---|---|
| `なの` | `<:syukka:1026820219039133696>` | false |
| `<:nano:1017766944180551690>` | 同上 | false |
| `なのだ` | 同上 | true |
| `なのです` | 同上 | true |

## 11. 自動リアクション

1. Bot 投稿または DM は無視する。
2. 投稿本文を正規化する。
3. guild の NG キーワードを取得し、一つでも含まれれば処理終了する。
4. guild の通常キーワードを取得する。
5. 正規化キーワードが本文に含まれる行ごとにリアクションを付与する。

## 12. リアクション付与

Unicode emoji はそのまま `message.add_reaction` する。
カスタム絵文字は `Add Reactions` 権限と `Use External Emojis` 権限を確認する。
Bot cache に絵文字があれば emoji object を使い、なければ mention 文字列で追加を試みる。
Discord error code `10014` は unknown emoji としてログ出力し、例外を再送出しない。
