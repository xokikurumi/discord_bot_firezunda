# 最新実装コマンド一覧

## 1. 作成元

この一覧は現在の Bot に実装されている `discord.py` コマンド定義を基に作成しています。

| 項目 | 内容 |
|---|---|
| 対象 | Cog に定義されたコマンド |
| コマンド方式 | `commands.hybrid_command`、`commands.hybrid_group` |
| prefix | `!` |
| slash command | 対応 |
| 生成日 | 2026-09-11 |

`hybrid_command` / `hybrid_group` で実装されているため、多くのコマンドは `!command` と `/command` の両方で利用できます。
ただし、slash command の反映は Discord 側の同期状態に依存します。

## 2. 権限区分

| 表記 | 内容 |
|---|---|
| 管理者 | `administrator` 権限が必要 |
| サーバー内利用者 | サーバー内で実行可能 |
| サーバー限定 | DM では利用不可 |

## 3. コマンド一覧

### 3.1 メッセージログ

実装ファイル: `cogs/messages/logs/message_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!backfill_message_logs [limit]` | `/backfill_message_logs limit:<count>` | 管理者 | 現在のサーバーの既存メッセージ履歴を `message_log` へ取り込む |

`limit` に `0` または未指定を指定した場合、取得可能な履歴を制限なしで取り込みます。

### 3.2 ダイスロール

実装ファイル: `cogs/messages/base/dice_roll_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!roll <expression>` | `/roll expression:<expression>` | サーバー内利用者 | `1d20`、`2d6+3` などのダイス式を振る |
| `!dice <expression>` | なし | サーバー内利用者 | `roll` の prefix alias |

メッセージ本文がダイス式だけの場合は、自動ロールも実行されます。

### 3.3 リアクション自動化

実装ファイル: `cogs/messages/base/message_reaction_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!reaction` | `/reaction` | サーバー限定 | 使用方法を表示する |
| `!reaction add <keyword> <reaction> [ng_word]` | `/reaction add keyword:<keyword> reaction:<reaction> ng_word:<true\|false>` | 管理者 | キーワードに対するリアクションまたは NG ワードルールを登録する |
| `!reaction remove <keyword>` | `/reaction remove keyword:<keyword>` | 管理者 | キーワードに一致するルールを削除する |
| `!reaction list` | `/reaction list` | サーバー内利用者 | 登録済みルールを一覧表示する |
| `!reaction check_emoji <emoji>` | `/reaction check_emoji emoji:<emoji>` | サーバー内利用者 | Bot がカスタム絵文字を参照・利用できるか確認する |
| `!reaction seed_syukka` | `/reaction seed_syukka` | 管理者 | 旧実装由来の `syukka` リアクションプリセットを登録する |

### 3.4 通知先設定

実装ファイル: `cogs/disaster/p2pquake_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!notify_config` | `/notify_config` | サーバー限定 | 使用方法を表示する |
| `!notify_config category` | `/notify_config category` | サーバー限定 | 通知カテゴリコマンドの使用方法を表示する |
| `!notify_config category list` | `/notify_config category list` | サーバー内利用者 | 利用可能な通知カテゴリを一覧表示する |
| `!notify_config add [#channel] [mention] [category]` | `/notify_config add channel:<channel> mention:<mention> category:<category>` | 管理者 | 通知カテゴリごとの通知先チャンネルを登録する |
| `!notify_config list` | `/notify_config list` | サーバー内利用者 | 現在のサーバーの通知先設定を一覧表示する |
| `!notify_config enable <id>` | `/notify_config enable config_id:<id>` | 管理者 | 通知先設定を有効化する |
| `!notify_config disable <id>` | `/notify_config disable config_id:<id>` | 管理者 | 通知先設定を無効化する |

`mention` は `none`、`なし`、`no` の場合にメンションなしとして扱われます。
`category` 未指定時は地震通知カテゴリが使用されます。

### 3.5 ICS 予定イベント連携

実装ファイル: `cogs/tasks/ics_guild_event_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!ics_event_sync` | `/ics_event_sync` | 管理者 | 現在のサーバーで ICS 予定イベント取り込みを手動実行する |
| `!ics_event_enable` | `/ics_event_enable` | 管理者 | 現在のサーバーで ICS 予定イベント取り込みを有効化する |
| `!ics_event_disable` | `/ics_event_disable` | 管理者 | 現在のサーバーで ICS 予定イベント取り込みを無効化する |
| `!ics_event_status` | `/ics_event_status` | 管理者 | 現在のサーバーの ICS 予定イベント取り込み状態を表示する |

`ics_event_sync` は、対象サーバーで ICS 連携が有効な場合のみ実行できます。

### 3.6 コミュニケーション傾向分析

実装ファイル: `cogs/tasks/communication_trend_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!communication_trend_analyze` | `/communication_trend_analyze` | 管理者 | 直近の完了済み半期を対象にコミュニケーション傾向分析を手動実行する |

slash command で実行した場合、開始・終了メッセージは ephemeral で送信されます。

### 3.7 Niconico Info

実装ファイル: `cogs/tasks/niconico_info_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!niconico_info_check` | `/niconico_info_check` | 管理者 | Niconico Info の取得・通知処理を手動実行する |
| `!niconico_info_filter` | `/niconico_info_filter` | 管理者 | フィルターコマンドの使用方法を表示する |
| `!niconico_info_filter add <keyword> [include\|exclude]` | `/niconico_info_filter add keyword:<keyword> mode:<include\|exclude>` | 管理者 | Niconico Info のキーワードフィルターを追加する |
| `!niconico_info_filter list` | `/niconico_info_filter list` | 管理者 | Niconico Info のキーワードフィルターを一覧表示する |
| `!niconico_info_filter enable <id>` | `/niconico_info_filter enable filter_id:<id>` | 管理者 | キーワードフィルターを有効化する |
| `!niconico_info_filter disable <id>` | `/niconico_info_filter disable filter_id:<id>` | 管理者 | キーワードフィルターを無効化する |
| `!niconico_info_filter remove <id>` | `/niconico_info_filter remove filter_id:<id>` | 管理者 | キーワードフィルターを削除する |

`mode` 未指定時は `include` として扱われます。

### 3.8 Niconico ユーザー投稿動画通知

実装ファイル: `cogs/tasks/niconico_user_video_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!niconico_user_video_check` | `/niconico_user_video_check` | 管理者 | 監視対象ユーザーの投稿動画確認を手動実行する |
| `!niconico_user_video_user` | `/niconico_user_video_user` | 管理者 | 監視ユーザーコマンドの使用方法を表示する |
| `!niconico_user_video_user add <user_id>` | `/niconico_user_video_user add user_id:<user_id>` | 管理者 | 監視対象の Niconico ユーザー ID を追加する |
| `!niconico_user_video_user list` | `/niconico_user_video_user list` | 管理者 | 監視対象の Niconico ユーザー ID を一覧表示する |
| `!niconico_user_video_user remove <id>` | `/niconico_user_video_user remove row_id:<id>` | 管理者 | 監視対象ユーザー行を無効化する |
| `!niconico_user_video_notify` | `/niconico_user_video_notify` | 管理者 | ユーザー別通知先コマンドの使用方法を表示する |
| `!niconico_user_video_notify add <user_id> [#channel] [mention]` | `/niconico_user_video_notify add user_id:<user_id> channel:<channel> mention:<mention>` | 管理者 | Niconico ユーザー別の通知先を登録する |
| `!niconico_user_video_notify list` | `/niconico_user_video_notify list` | 管理者 | Niconico ユーザー別の通知先設定を一覧表示する |
| `!niconico_user_video_notify enable <id>` | `/niconico_user_video_notify enable config_id:<id>` | 管理者 | Niconico ユーザー別通知先設定を有効化する |
| `!niconico_user_video_notify disable <id>` | `/niconico_user_video_notify disable config_id:<id>` | 管理者 | Niconico ユーザー別通知先設定を無効化する |

`channel` 未指定時は、コマンドを実行したチャンネルが通知先になります。

### 3.9 Ollama メッセージ分析

実装ファイル: `cogs/messages/base/analysis_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!analysis` | `/analysis` | サーバー限定 | 分析管理コマンドの使用方法を表示する |
| `!analysis feedback <message_id> <label> [reason_tag] [note]` | `/analysis feedback message_id:<id> label:<label> reason_tag:<reason_tag> note:<note>` | 管理者 | 保存済み分析結果に対する管理者フィードバックと理由タグを登録する |
| `!analysis whitelist` | `/analysis whitelist` | 管理者 | 分析除外ルールコマンドの使用方法を表示する |
| `!analysis whitelist add <text_exact\|text_contains\|user\|channel> <pattern>` | `/analysis whitelist add rule_type:<type> pattern:<pattern>` | 管理者 | 分析除外ルールを追加する |
| `!analysis whitelist list [all]` | `/analysis whitelist list include_disabled:<all>` | 管理者 | 分析除外ルールを一覧表示する |
| `!analysis whitelist enable <id>` | `/analysis whitelist enable rule_id:<id>` | 管理者 | 分析除外ルールを有効化する |
| `!analysis whitelist disable <id>` | `/analysis whitelist disable rule_id:<id>` | 管理者 | 分析除外ルールを無効化する |

`label` は `correct`、`false_positive`、`false_negative`、`unsure` とそれぞれの alias を受け付けます。
`reason_tag` は次の値を受け付けます。

- `unspecified`
- `meme`
- `inside_joke`
- `game_context`
- `external_news_comment`
- `external_criticism`
- `sexual_banter`
- `roleplay`
- `quote`
- `direct_attack`
- `intimidation`
slash command では label と reason tag が日本語補足付きの選択肢として表示されます。
prefix command で reason tag として解釈できない第 3 引数は、従来互換のため note として扱われます。
`user` と `channel` の除外ルールは Discord ID を指定します。

### 3.10 リアクション抽選

実装ファイル: `cogs/messages/base/reaction_lottery_cog.py`

| コマンド | slash command | 権限 | 用途 |
|---|---|---|---|
| `!lottery` | `/lottery` | サーバー限定 | 抽選コマンドの使用方法を表示する |
| `!lottery start [winners] [end] [emoji] [title]` | `/lottery start winners:<count> end:<duration_or_datetime> title:<emoji_and_title>` | サーバー内利用者 | 応募リアクションによる抽選を開始する |
| `!lottery end <message_id>` | `/lottery end message_id:<id>` | 作成者またはメッセージ管理権限 | 実行中の抽選を早期終了する |

`end` は `30m`、`2h`、`1d` などの相対時間、または `YYYY-MM-DD HH:MM` 形式などの日時を受け付けます。
終了時刻は未来かつ 7 日以内である必要があります。
`title` の先頭が絵文字またはカスタム絵文字の場合、その値を応募リアクションとして使用します。

## 4. コマンドではない自動処理

以下は Discord コマンドではありませんが、Cog の listener または background task として実装されています。

| 処理 | 実装ファイル | 内容 |
|---|---|---|
| メッセージ作成ログ | `cogs/messages/logs/message_cog.py` | 新規メッセージを `message_log` に保存する |
| メッセージ編集ログ | `cogs/messages/logs/message_cog.py` | 編集イベントを `message_edit_log` に保存する |
| メッセージ削除ログ | `cogs/messages/logs/message_cog.py` | 削除イベントを `message_delete_log` に保存する |
| ダイス式自動ロール | `cogs/messages/base/dice_roll_cog.py` | メッセージ本文がダイス式のみの場合に自動でロールする |
| リアクション自動付与 | `cogs/messages/base/message_reaction_cog.py` | 登録済みキーワードに一致するメッセージへリアクションする |
| P2PQuake 監視 | `cogs/disaster/p2pquake_cog.py` | P2PQuake WebSocket を監視し、通知先設定に従って通知する |
| ICS 定期取り込み | `cogs/tasks/ics_guild_event_cog.py` | 有効化済みサーバーの ICS 予定を定期取り込みする |
| コミュニケーション傾向定期分析 | `cogs/tasks/communication_trend_cog.py` | 半期ごとの分析対象時期に傾向分析を実行する |
| Niconico Info 定期確認 | `cogs/tasks/niconico_info_cog.py` | Niconico Info の対象 URL を定期確認する |
| Niconico 投稿動画定期確認 | `cogs/tasks/niconico_user_video_cog.py` | 監視対象ユーザーの投稿動画を定期確認する |
| Ollama メッセージ分析 | `cogs/messages/base/message_watcher_cog.py` | 投稿メッセージを分析し、結果保存・リアクション・通知を行う |

## 5. 集計

| 区分 | 件数 |
|---|---:|
| 直接実行できるコマンド行 | 46 |
| 自動処理 | 11 |
