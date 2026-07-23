# Niconico Info 通知詳細

## 1. 目的

設定された Niconico Info / niconews ページを定期的に取得し、新しい記事または投稿祭イベントを検出して通知する。guild ごとの include/exclude フィルタで通知対象を制御する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| NiconicoInfoCog | background task と検出/フィルタ管理コマンドを提供する |
| NiconicoInfoService | HTML 取得、解析、重複判定、通知、要約を行う |
| NiconicoInfoEventData | 検出イベント DTO |
| NiconicoInfoEventRepository | 検出済み/送信済みイベントを管理する |
| NiconicoInfoFilterRepository | guild ごとの include/exclude keyword を管理する |
| NotifyChannelConfigRepository | `NICONICO_INFO` 通知先を取得する |

## 3. 定期実行

機能が無効なら終了する。有効なら Bot ready 後、即時 `check_once` を実行し、その後 `NICONICO_INFO_CHECK_INTERVAL_SECONDS` ごとに繰り返す。

## 4. コマンド

| コマンド | 権限 | 処理 |
|---|---|---|
| `niconico_info_check` | 管理者 | 手動検出と通知 |
| `niconico_info_filter` | 管理者 | usage |
| `niconico_info_filter add <keyword> [include\|exclude]` | 管理者 | フィルタ追加 |
| `niconico_info_filter list` | 管理者 | guild フィルタ一覧 |
| `niconico_info_filter enable <id>` | 管理者 | フィルタ有効化 |
| `niconico_info_filter disable <id>` | 管理者 | フィルタ無効化 |
| `niconico_info_filter remove <id>` | 管理者 | フィルタ soft delete |

mode は `exclude`、`ng`、`deny`、`除外` の場合 exclude、それ以外は include とする。

## 5. check_once

1. target URLs を取得してイベントを検出する。
2. 未送信イベントを通知する。
3. 全体例外はログ出力して終了する。

## 6. HTML 取得

各 target URL を `User-Agent: discord_bot_v3` 付き、30 秒 timeout で取得し、UTF-8 decode する。URL 単位の取得失敗は warning にして他 URL を継続する。

## 7. ブログ記事解析

`li.l-main-list2-item` を走査する。
最初の anchor href が `https://blog.nicovideo.jp/niconews/{数字}/` に一致するものだけ対象にする。
同一 link は 1 回だけ処理する。

anchor text の末尾に `YYYY-MM-DD` がある場合は title と published date に分割する。
カテゴリ名は `.category-title`、`h1`、`h2` の順に最初の空でない text を使用する。

## 8. 投稿祭イベント解析

ブログ形式が 1 件以上解析できた場合はブログ結果を優先する。ブログ結果がない場合、`div.events-Content ul.sw-List li.list-Item`、なければ `li.list-Item` を対象にする。

各 article から次を抽出する。

| 項目 | 取得元 |
|---|---|
| title | `div.item-Info p.title` または `p.title` |
| date_text | `div.item-Info p.date` または `p.date` |
| explanation | `div.item-Info p.text` または `p.text` |
| organizer_user | `div.item-Info a.text-Link` または `a.text-Link` |
| organizer_link | organizer anchor href |
| link | btn list のうち label に `告知動画` を含む href、なければ先頭 btn href |
| categories | category list の text |

date_text から `YYYY年M月D日 ... YYYY年M月D日` を抽出できる場合、start/end date を date 型にする。

## 9. 重複 key

source key は title、start date、end date、link、organizer link を連結して作る。
連結文字列を UTF-8 で SHA-256 hash 化した hex 文字列とする。
同一 check 内でも source key 重複を除外する。DB に source key が存在する場合は保存しない。

## 10. 保存

新規イベントは source key、title、start/end date、date text、explanation、link を保存する。
organizer user/link、categories の comma join、source URL、`send_flg=False` も保存する。

## 11. フィルタ判定

通知対象テキストは title、date text、explanation、link、organizer user/link、categories、source URL を改行結合し casefold する。

1. 有効フィルタがない場合は通知対象。
2. exclude フィルタの keyword が含まれる場合は通知しない。
3. include フィルタが 1 件以上ある場合は、いずれかの keyword が含まれる場合のみ通知。
4. include フィルタがない場合は通知対象。

## 12. 通知

未送信イベントごとに、各 guild の `NICONICO_INFO` 有効通知設定と有効フィルタを取得する。
通知設定がある guild は handled とみなす。フィルタに通った場合、各通知先 channel へ送信する。
通知に成功した、または通知設定がある guild により handled された場合、イベントを sent に更新する。

本文はタイトル、期間、主催、カテゴリ、link、要約を含め、1900 文字以内に切り詰める。

## 13. 要約

explanation があれば空白正規化して最大 500 文字に丸める。
explanation がない場合、link または organizer link を取得して記事本文を抽出する。
script/style/noscript/header/footer/nav を除去後、主要本文候補を順に探索する。
article、entry-content、articleBody、article-body、post-content、l-main、main、body の順に確認する。
80 文字以上の本文を探して要約する。取得失敗は warning にして要約なしで通知する。
