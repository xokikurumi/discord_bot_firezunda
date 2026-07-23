# Niconico ユーザー投稿通知詳細

## 1. 目的

監視対象の Niconico ユーザーについて、通常動画とショート動画の最新投稿を検出し、未通知の投稿を guild ごとの通知先へ送信する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| NiconicoUserVideoCog | background task と監視/通知設定コマンドを提供する |
| NiconicoUserVideoService | 投稿検出、送信済み管理、通知を行う |
| NiconicoVideo | user id、title、link、pub date を持つ DTO |
| NiconicoUserVideoInfoRepository | 監視対象ユーザーを管理する |
| NiconicoVideoSendLogRepository | 検出済み/送信済み動画を管理する |
| NiconicoNotifyChannelConfigRepository | ユーザー別通知先を管理する |

## 3. 定期実行

機能が無効な場合は終了する。有効な場合は Bot ready 後、15 分境界で繰り返し実行する。次回実行までの秒数は、現在分秒を 900 秒で割った余りを使い、`900 - remainder` とする。余りが 0 の場合は 0 秒後。

## 4. コマンド

| コマンド | 権限 | 処理 |
|---|---|---|
| `niconico_user_video_check` | 管理者 | 手動検出と通知 |
| `niconico_user_video_user` | 管理者 | usage |
| `niconico_user_video_user add <user_id>` | 管理者 | 監視ユーザー追加 |
| `niconico_user_video_user list` | 管理者 | 有効な監視ユーザー一覧 |
| `niconico_user_video_user remove <id>` | 管理者 | 監視ユーザーを無効化 |
| `niconico_user_video_notify` | 管理者 | usage |
| `niconico_user_video_notify add <user_id> [#channel] [mention]` | 管理者 | ユーザー別通知先追加 |
| `niconico_user_video_notify list` | 管理者 | guild の通知先一覧 |
| `niconico_user_video_notify enable <id>` | 管理者 | 通知先有効化 |
| `niconico_user_video_notify disable <id>` | 管理者 | 通知先無効化 |

通知先追加時、channel 省略時はコマンド実行チャンネルを使用する。mention が `none`、`なし`、`no` の場合は空にする。

## 5. check_once

1. 監視対象ユーザーの最新投稿を検出する。
2. 未送信動画を通知する。
3. 全体例外はログ出力して終了する。

## 6. 投稿検出

DB から有効な user id を取得する。
各 user id について通常動画 API とショートページを取得し、結果を投稿日降順で統合する。
各動画 link が既に送信ログに存在する場合は skip する。
存在しない場合は `user_id`、`link`、`title`、`pub_date`、`send_flg=False` を保存する。

## 7. 通常動画取得

API URL は user id を埋め込み、`sortKey=registeredAt`、`sortOrder=desc` を指定する。
`pageSize=1`、`page=1` も指定する。
header は `User-Agent: discord_bot_v3`、`X-Frontend-Id: 6`、`X-Frontend-Version: 0`。

payload の `data.items[0].essential` から `id` と `title` を取得する。
どちらかが欠ける場合は null とする。
link は `https://www.nicovideo.jp/watch/{id}`、pub date は `registeredAt`。

## 8. ショート動画取得

`https://www.nicovideo.jp/user/{user_id}/shorts` を HTML として取得する。BeautifulSoup で script、`data-initial-data`、anchor を解析する。

JSON payload からは再帰的に `id`、`videoId`、`contentId`、`watchId` を動画 id 候補とする。
`title` または `name` を title とする。
`registeredAt`、`createdAt`、`publishedAt`、`uploadTime`、`datePublished` を pub date 候補とする。
anchor は href から `(sm|so|nm|ss)\d+` を抽出する。
title 属性、text、video id の順で title を決める。近傍の time タグがあれば pub date にする。

同一 link は後勝ちで 1 件にし、pub date の datetime parse 結果が最大のものを最新ショートとする。

## 9. 通知

未送信ログを取得し、各 guild で対象 user id の有効通知設定を取得する。
同一 `(channel_id, mention)` は重複送信しない。channel が見つからない場合は warning ログを出す。
1 つ以上送信できた場合のみ送信ログを sent に更新する。

通知本文は「ニコニコ動画に新しい動画が投稿されました。」、タイトル、投稿時間、link を改行結合する。
投稿時間は ISO datetime を JST に変換し、`YYYY/MM/DD HH:MM:SS` 形式にする。
parse できない場合は元文字列を表示する。

## 10. メンション

mention は共通通知設定と同じく、`everyone`、`here`、既存 mention、数字 role id、その他文字列を解釈する。
