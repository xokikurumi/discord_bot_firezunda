# リアクションコマンド一覧（旧実装起こし）

## 参照元

旧実装からリアクション関連のコマンド候補を抽出した一覧です。

| 参照ファイル | 内容 |
|---|---|
| `common/commands.py` | `configCmd` 内にコメントとして残っている設定コマンド案 |
| `main.py` | メッセージ内容に応じた固定リアクション付与処理 |
| `commands/fireconfig.py` | `/fireconfig` スラッシュコマンド定義。ただしリアクション設定ではなく疎通確認系 |

## 旧実装で確認できたリアクション関連コマンド

旧実装では、リアクション設定コマンドは `common/commands.py` にコメントとして残っており、実処理は未実装でした。
現在実装へ起こす場合は、以下をリアクション管理コマンドの元仕様として扱います。

| コマンド | 引数 | 用途 | 旧実装での状態 |
|---|---|---|---|
| `addReaction` | `<正規表現> <絵文字>` | 条件に一致したメッセージへリアクションを付与するルールを登録する | コメントのみ |
| `addNgReaction` | `<正規表現> <絵文字>` | リアクション対象外または抑止用のNGリアクションルールを登録する | コメントのみ |
| `listReaction` | なし | 登録済みリアクションルールを一覧表示する | コメントのみ |
| `removeReaction` | `<ID または条件>` | 登録済みリアクションルールを削除する | コメントのみ |

## 旧実装で関連していたがリアクション以外のコマンド

`common/commands.py` には返信、RSS、通知先設定などのコマンド案も同じ場所に残っています。
リアクション機能と混同しやすいため、別機能として扱います。

| コマンド | 引数 | 用途 | 分類 |
|---|---|---|---|
| `addReply` | `<正規表現> <返信文>` | 自動返信ルール登録 | 自動返信 |
| `addNgReply` | `<正規表現> <返信文>` | NG返信ルール登録 | 自動返信 |
| `listReply` | なし | 自動返信ルール一覧 | 自動返信 |
| `listNgReply` | なし | NG返信ルール一覧 | 自動返信 |
| `removeReply` | `<ID または条件>` | 自動返信ルール削除 | 自動返信 |
| `removeNgReply` | `<ID または条件>` | NG返信ルール削除 | 自動返信 |
| `addRss` | `<URL> <channelID> [正規表現]` | RSS通知登録 | RSS通知 |
| `listRss` | なし | RSS通知一覧 | RSS通知 |
| `removeRss` | `<ID>` | RSS通知削除 | RSS通知 |
| `setQuekeChannel` | `<channelID>` | 地震情報の送信先チャンネル設定 | 通知設定 |
| `setQuekeMention` | `<mention>` | 地震情報のメンション設定 | 通知設定 |
| `setNicoMenteChannel` | `<channelID>` | ニコニコメンテ情報の送信先チャンネル設定 | 通知設定 |
| `setNicoMenteMention` | `<mention>` | ニコニコメンテ情報のメンション設定 | 通知設定 |
| `setSyntheticChannel` | `<channelID>` | 合成音声関連情報の送信先チャンネル設定 | 通知設定 |
| `setSyntheticMention` | `<mention>` | 合成音声関連情報のメンション設定 | 通知設定 |
| `setChannel` | `<channelID>` | 汎用送信先チャンネル設定 | 通知設定 |
| `setMention` | `<mention>` | 汎用メンション設定 | 通知設定 |

## 旧実装の固定リアクション処理

`main.py` には、コマンドではなくメッセージ受信時の固定リアクション処理があります。
特定の文字列やカスタム絵文字に一致した場合、次のリアクションを付与していました。

| 条件 | 付与リアクション | 備考 |
|---|---|---|
| `nano` 系の表記または `<:nano:1017766944180551690>` を含むメッセージ | `<:syukka:1026820219039133696>` | 一部NG表現に一致する場合は付与しない |

この固定リアクションは、現行実装では `reaction seed_syukka` のプリセット登録に近い扱いです。

## 現行実装へ対応させる場合のコマンド対応

旧実装のコメント上のコマンドを、現行実装の `reaction` コマンドへ対応させると以下の通りです。

| 旧コマンド | 現行コマンド案 | 備考 |
|---|---|---|
| `addReaction <正規表現> <絵文字>` | `!reaction add <keyword> <reaction> false` / `/reaction add` | 現行実装はキーワード一致。正規表現対応は別途検討 |
| `addNgReaction <正規表現> <絵文字>` | `!reaction add <keyword> <reaction> true` / `/reaction add ng_word:true` | NGワード一致時は通常リアクションを抑止 |
| `listReaction` | `!reaction list` / `/reaction list` | 現行実装済み |
| `removeReaction <条件>` | `!reaction remove <keyword>` / `/reaction remove` | 現行実装はキーワード指定で削除 |

## 現行実装で利用できるリアクションコマンド

| コマンド | 権限 | 用途 |
|---|---|---|
| `!reaction add <keyword> <reaction> [ng_word]` | 管理者 | リアクションまたはNGワードルールを登録する |
| `/reaction add keyword:<keyword> reaction:<reaction> ng_word:<true\|false>` | 管理者 | リアクションまたはNGワードルールを登録する |
| `!reaction remove <keyword>` | 管理者 | キーワードに一致するルールを削除する |
| `/reaction remove keyword:<keyword>` | 管理者 | キーワードに一致するルールを削除する |
| `!reaction list` | サーバー内利用者 | 登録済みルールを一覧表示する |
| `/reaction list` | サーバー内利用者 | 登録済みルールを一覧表示する |
| `!reaction check_emoji <emoji>` | サーバー内利用者 | Botがカスタム絵文字を参照・利用できるか確認する |
| `/reaction check_emoji emoji:<emoji>` | サーバー内利用者 | Botがカスタム絵文字を参照・利用できるか確認する |
| `!reaction seed_syukka` | 管理者 | 旧実装の `syukka` 固定リアクション相当のプリセットを登録する |
| `/reaction seed_syukka` | 管理者 | 旧実装の `syukka` 固定リアクション相当のプリセットを登録する |
