# 通知設定詳細

## 1. 目的

災害通知、即売会イベント、Niconico Info など複数機能で共通利用する通知先チャンネル、メンション、カテゴリ、有効状態を管理する。

## 2. 通知カテゴリ

| カテゴリ | 用途 |
|---|---|
| `QUAKE` | P2PQuake / earthquake notifications |
| `SALES_EVENT` | ICS scheduled event import notifications |
| `NICONICO_INFO` | Niconico Info / niconews notifications |
| `NICONICO_USER_VIDEO` | Niconico user upload notifications use per-user settings |

`EEW` 相当は `QUAKE` と同一カテゴリとして扱う。

## 3. コマンド

通知設定コマンドは `notify_config` グループで提供する。参照系は guild 限定、更新系は管理者権限を要求する。

| コマンド | 権限 | 処理 |
|---|---|---|
| `notify_config` | guild | usage を表示 |
| `notify_config category list` | guild | 利用可能カテゴリを一覧表示 |
| `notify_config add [#channel] [mention] [category]` | 管理者 | 通知設定を追加 |
| `notify_config list` | guild | guild の通知設定を一覧表示 |
| `notify_config enable <id>` | 管理者 | 通知設定を有効化 |
| `notify_config disable <id>` | 管理者 | 通知設定を無効化 |

## 4. 追加処理

`add` では channel が省略された場合、コマンド実行チャンネルを使用する。mention が `none`、`なし`、`no` の場合は空文字に変換する。category は大文字化して保存する。

保存項目は `category`、`guild_id`、`channel_id`、`enabled=True`、`mention` とする。

## 5. 一覧処理

guild に紐づく通知設定を取得する。
channel が Bot cache で取得できる場合は mention 表記、取得できない場合は channel id 文字列で表示する。
Discord メッセージ長を考慮し、1900 文字を超える前に分割送信する。

## 6. 有効/無効

`enable` / `disable` は guild id と config id で対象を絞る。
更新件数が 0 の場合は `notify config not found: id={id}` を返す。
更新できた場合は enabled/disabled メッセージを返す。

## 7. メンション構築

通知送信時の mention は次のルールで構築する。

| DB 値 | 出力 |
|---|---|
| 空 | 空文字 |
| `everyone` | `@everyone` |
| `here` | `@here` |
| `<@` で始まる値 | そのまま |
| 数字のみ | role mention `<@&{id}>` |
| その他 | そのまま |
