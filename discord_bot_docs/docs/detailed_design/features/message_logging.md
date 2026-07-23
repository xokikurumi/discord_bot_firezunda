# メッセージログ詳細

## 1. 目的

サーバー内のメッセージ作成、編集、削除を DB に保存し、履歴取り込みコマンドで過去ログを重複なく補完する。投稿時には添付ファイルをローカル保存し、ユーザー/チャンネルの最新マスタ情報も更新する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| MessageCog | Discord listener と履歴取り込みコマンドを提供する |
| MessageLogService | メッセージイベントを DB 行へ変換する |
| MessageLogRepository | 投稿ログの insert、insert ignore、検索を行う |
| MessageEditLogRepository | 編集履歴を保存/取得する |
| MessageDeleteLogRepository | 削除履歴を保存/取得する |
| DiscordUserRepository | guild/user の最新ユーザー属性を upsert する |
| DiscordChannelRepository | guild/channel の最新チャンネル属性を upsert する |

## 3. コマンド

| コマンド | 権限 | 処理 |
|---|---|---|
| `backfill_message_logs [limit]` | guild 限定、管理者 | guild 内の全 text channel から履歴を古い順に取得し、未保存メッセージを追加する |

`limit <= 0` の場合は Discord API の履歴取得 limit を `None` とし、全件対象にする。500 件走査ごとに進捗を送信する。閲覧権限または履歴閲覧権限がない channel は失敗一覧に記録して続行する。

## 4. リアルタイム投稿保存

1. `on_message` が発火する。
2. guild がない DM は無視する。
3. Service の `log_create` を呼び出す。
4. 添付ファイル保存先を `files/{guild_id}/{channel_id}/{message_id}` とする。
5. 添付ファイルを添付順 index と元拡張子で保存する。
6. ユーザー/チャンネルマスタを upsert する。
7. `message_log` に投稿ログを insert する。

## 5. 投稿ログ項目

| 項目 | 値 |
|---|---|
| message_id | Discord message id |
| guild_id | message.guild.id |
| channel_id | message.channel.id |
| user_id | message.author.id |
| content | message.content |
| message_created_at | message.created_at |
| bot_flg | message.author.bot |
| has_attachments | 添付ファイルが 1 件以上 |
| has_embeds | embed が 1 件以上 |
| has_stickers | sticker が 1 件以上 |
| stickers | sticker の id/name/format/url を JSON 文字列化、ない場合 null |

## 6. ユーザーマスタ upsert

投稿者から guild/user の識別子、表示名、Bot 判定、avatar URL、最終確認日時を作成する。
avatar は `display_avatar` を優先し、なければ `avatar` を使用する。

## 7. チャンネルマスタ upsert

チャンネルから guild/channel の識別子、名前、種別、カテゴリ、親 channel、表示順、最終確認日時を作成する。
parent がない場合 `parent_channel_id` は null とする。

## 8. 履歴取り込み

履歴取り込みは添付ファイルを保存しない。
マスタ upsert と `message_log` の insert ignore のみ行う。
insert ignore が成功した場合は inserted、重複などで挿入されない場合は skipped として集計する。

## 9. 編集ログ

### キャッシュあり編集

`on_message_edit(before, after)` では guild なしを無視する。
`message_edit_log` には message/guild/channel/user の id と、編集前後の content を保存する。

### キャッシュなし編集

`on_raw_message_edit(payload)` では `payload.cached_message` がある場合は通常編集で処理済みとして無視する。
channel を取得できない場合は無視する。
message を fetch し、既存編集履歴があれば最新編集履歴の `after_content` を before とする。
編集履歴がなければ投稿ログの content を before とする。どちらもない場合 before は null とする。

## 10. 削除ログ

### キャッシュあり削除

`on_message_delete(message)` では guild なしを無視する。
`message_delete_log` には message/guild/channel/user/content/bot/添付有無/embed 有無を保存する。

### キャッシュなし削除

`on_raw_message_delete(payload)` では `payload.cached_message` がある場合は通常削除で処理済みとして無視する。
guild_id がない場合は無視する。
payload から message/guild/channel id のみ保存し、user/content/bot/添付/embed は null とする。

## 11. 例外処理

各 listener では Service 呼び出し全体を try/catch し、例外をログ出力して Bot を継続する。履歴取り込みコマンドは権限不足、DM 実行、その他例外を Discord 応答に変換する。
