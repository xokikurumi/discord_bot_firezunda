# DBテーブル定義書

生成日時: 2026-07-12 00:06:13
文字コード: UTF-8
対象DB: `discordbot_v2`

## テーブル一覧

- `b_geolonia_address`: Geolonia住所データ。地震観測地点などの住所から緯度経度を検索するために使用します。
- `b_geolonia_sync_state`: Geolonia住所データの同期状態を管理します。
- `b_jma_shindo_station`: 気象庁震度観測点データ。観測地点の緯度経度検索に使用します。
- `b_jma_sync_state`: 気象庁震度観測点データの同期状態を管理します。
- `b_m_niconico_video_infomation`: ニコニコ動画ユーザ投稿通知の監視対象ユーザを管理します。
- `b_niconico_notify_cannel_config`: ニコニコ動画ユーザごとの通知先チャンネル設定を管理します。
- `b_niconico_video_send_log`: ニコニコ動画ユーザ投稿通知の検出結果と送信済み状態を管理します。
- `b_notify_cannel_config`: 汎用通知カテゴリごとの通知先チャンネル設定を管理します。
- `b_reaction_keywords`: キーワードに応じた自動リアクション設定を管理します。
- `communication_trend_analysis`: 半期ごとのコミュニケーション傾向分析結果を保存します。
- `ics_guild_event_config`: ICS予定イベント取り込みのギルド別有効/無効設定を管理します。
- `ics_guild_event_import`: ICS予定イベントの取り込み済み状態を管理します。
- `message_analysis_log`: Ollamaによるメッセージ解析結果を保存します。
- `message_delete_log`: Discordメッセージ削除ログを保存します。
- `message_edit_log`: Discordメッセージ編集ログを保存します。
- `message_log`: Discordメッセージ投稿ログを保存します。
- `niconico_info_event`: ニコニコインフォ通知対象記事と送信状態を管理します。
- `niconico_info_filter`: ニコニコインフォ通知フィルターを管理します。
- `voice_status_log`: Discordボイス状態変更ログを保存します。

## `b_geolonia_address`

Geolonia住所データ。地震観測地点などの住所から緯度経度を検索するために使用します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `prefecture` | `varchar(50)` | 不可 |  | 索引 |  |  |
| 3 | `municipality` | `varchar(100)` | 不可 |  | 索引 |  |  |
| 4 | `town` | `varchar(150)` | 不可 |  | 索引 |  |  |
| 5 | `lat` | `float` | 不可 |  |  |  |  |
| 6 | `lng` | `float` | 不可 |  |  |  |  |
| 7 | `source_updated_at` | `datetime` | 可 |  |  |  |  |
| 8 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_geolonia_address_municipality` | いいえ | `municipality` |
| `ix_b_geolonia_address_prefecture` | いいえ | `prefecture` |
| `ix_b_geolonia_address_town` | いいえ | `town` |
| `uq_geolonia_address` | はい | `prefecture`, `municipality`, `town` |

### 外部キー

外部キーはありません。

## `b_geolonia_sync_state`

Geolonia住所データの同期状態を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `name` | `varchar(100)` | 不可 |  | 一意キー |  |  |
| 3 | `last_synced_at` | `datetime` | 可 |  |  |  |  |
| 4 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `uq_geolonia_sync_state_name` | はい | `name` |

### 外部キー

外部キーはありません。

## `b_jma_shindo_station`

気象庁震度観測点データ。観測地点の緯度経度検索に使用します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `region_name` | `varchar(100)` | 不可 |  | 索引 |  |  |
| 3 | `station_name` | `varchar(150)` | 不可 |  | 索引 |  |  |
| 4 | `address` | `text` | 可 |  |  |  |  |
| 5 | `lat` | `float` | 不可 |  |  |  |  |
| 6 | `lng` | `float` | 不可 |  |  |  |  |
| 7 | `observation_start` | `varchar(20)` | 可 |  |  |  |  |
| 8 | `observation_end` | `varchar(20)` | 可 |  | 索引 |  |  |
| 9 | `source_updated_at` | `datetime` | 可 |  |  |  |  |
| 10 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_jma_shindo_station_observation_end` | いいえ | `observation_end` |
| `ix_b_jma_shindo_station_region_name` | いいえ | `region_name` |
| `ix_b_jma_shindo_station_station_name` | いいえ | `station_name` |
| `uq_jma_shindo_station_name_lat_lng` | はい | `station_name`, `lat`, `lng` |

### 外部キー

外部キーはありません。

## `b_jma_sync_state`

気象庁震度観測点データの同期状態を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `name` | `varchar(100)` | 不可 |  | 一意キー |  |  |
| 3 | `last_synced_at` | `datetime` | 可 |  |  |  |  |
| 4 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `uq_jma_sync_state_name` | はい | `name` |

### 外部キー

外部キーはありません。

## `b_m_niconico_video_infomation`

ニコニコ動画ユーザ投稿通知の監視対象ユーザを管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `delete_flg` | `tinyint(1)` | 不可 |  | 索引 |  |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_m_niconico_video_infomation_delete_flg` | いいえ | `delete_flg` |
| `ix_b_m_niconico_video_infomation_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。

## `b_niconico_notify_cannel_config`

ニコニコ動画ユーザごとの通知先チャンネル設定を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `guild_id` | `bigint` | 可 |  | 索引 |  |  |
| 4 | `channel_id` | `bigint` | 不可 |  |  |  |  |
| 5 | `enabled` | `tinyint(1)` | 不可 |  |  |  |  |
| 6 | `mention` | `text` | 可 |  |  |  |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_niconico_notify_cannel_config_guild_id` | いいえ | `guild_id` |
| `ix_b_niconico_notify_cannel_config_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。

## `b_niconico_video_send_log`

ニコニコ動画ユーザ投稿通知の検出結果と送信済み状態を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `link` | `text` | 不可 |  |  |  |  |
| 4 | `title` | `text` | 不可 |  |  |  |  |
| 5 | `pub_date` | `varchar(100)` | 可 |  |  |  |  |
| 6 | `send_flg` | `tinyint(1)` | 不可 |  | 索引 |  |  |
| 7 | `delete_flg` | `tinyint(1)` | 不可 |  | 索引 |  |  |
| 8 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_niconico_video_send_log_delete_flg` | いいえ | `delete_flg` |
| `ix_b_niconico_video_send_log_send_flg` | いいえ | `send_flg` |
| `ix_b_niconico_video_send_log_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。

## `b_notify_cannel_config`

汎用通知カテゴリごとの通知先チャンネル設定を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `category` | `varchar(50)` | 不可 |  | 索引 |  |  |
| 3 | `guild_id` | `bigint` | 可 |  | 索引 |  |  |
| 4 | `channel_id` | `bigint` | 不可 |  |  |  |  |
| 5 | `enabled` | `tinyint(1)` | 不可 |  |  |  |  |
| 6 | `mention` | `text` | 可 |  |  |  |  |
| 7 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_notify_cannel_config_category` | いいえ | `category` |
| `ix_b_notify_cannel_config_guild_id` | いいえ | `guild_id` |

### 外部キー

外部キーはありません。

## `b_reaction_keywords`

キーワードに応じた自動リアクション設定を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `enabled` | `tinyint(1)` | 不可 |  |  |  |  |
| 4 | `keyword` | `text` | 不可 |  |  |  |  |
| 5 | `reaction` | `text` | 可 |  |  |  |  |
| 6 | `reaction_id` | `bigint` | 可 |  |  |  |  |
| 7 | `reaction_animation_flg` | `tinyint(1)` | 可 |  |  |  |  |
| 8 | `ng_word_flg` | `tinyint(1)` | 可 |  |  |  |  |
| 9 | `delete_flg` | `tinyint(1)` | 可 |  |  |  |  |
| 10 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_b_reaction_keywords_guild_id` | いいえ | `guild_id` |

### 外部キー

外部キーはありません。

## `communication_trend_analysis`

半期ごとのコミュニケーション傾向分析結果を保存します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `period_key` | `varchar(20)` | 不可 |  | 索引 |  |  |
| 3 | `period_start` | `datetime` | 不可 |  |  |  |  |
| 4 | `period_end` | `datetime` | 不可 |  |  |  |  |
| 5 | `scope_type` | `varchar(20)` | 不可 |  | 索引 |  |  |
| 6 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 7 | `user_id` | `bigint` | 可 |  | 索引 |  |  |
| 8 | `model` | `varchar(100)` | 不可 |  |  |  |  |
| 9 | `message_count` | `int` | 不可 |  |  |  |  |
| 10 | `edit_count` | `int` | 不可 |  |  |  |  |
| 11 | `delete_count` | `int` | 不可 |  |  |  |  |
| 12 | `analysis_count` | `int` | 不可 |  |  |  |  |
| 13 | `max_score_avg` | `int` | 不可 |  |  |  |  |
| 14 | `metrics` | `text` | 可 |  |  |  |  |
| 15 | `summary` | `text` | 可 |  |  |  |  |
| 16 | `tendencies` | `text` | 可 |  |  |  |  |
| 17 | `risks` | `text` | 可 |  |  |  |  |
| 18 | `recommendations` | `text` | 可 |  |  |  |  |
| 19 | `raw_result` | `text` | 可 |  |  |  |  |
| 20 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `idx_comm_trend_guild_created` | いいえ | `guild_id`, `created_at` |
| `idx_comm_trend_period_scope` | いいえ | `period_key`, `scope_type`, `guild_id`, `user_id` |
| `idx_comm_trend_user_created` | いいえ | `user_id`, `created_at` |
| `ix_communication_trend_analysis_guild_id` | いいえ | `guild_id` |
| `ix_communication_trend_analysis_period_key` | いいえ | `period_key` |
| `ix_communication_trend_analysis_scope_type` | いいえ | `scope_type` |
| `ix_communication_trend_analysis_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。

## `ics_guild_event_config`

ICS予定イベント取り込みのギルド別有効/無効設定を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `guild_id` | `bigint` | 不可 |  | 一意キー |  |  |
| 3 | `enabled` | `tinyint(1)` | 不可 | 0 |  |  |  |
| 4 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_ics_guild_event_config_guild_id` | いいえ | `guild_id` |
| `uq_ics_guild_event_config_guild_id` | はい | `guild_id` |

### 外部キー

外部キーはありません。

## `ics_guild_event_import`

ICS予定イベントの取り込み済み状態を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `ics_uid` | `varchar(255)` | 不可 |  |  |  |  |
| 4 | `source_url` | `text` | 不可 |  |  |  |  |
| 5 | `scheduled_event_id` | `bigint` | 可 |  |  |  |  |
| 6 | `summary` | `text` | 可 |  |  |  |  |
| 7 | `start_time` | `datetime` | 不可 |  |  |  |  |
| 8 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_ics_guild_event_import_guild_id` | いいえ | `guild_id` |
| `uq_ics_guild_event_import_guild_uid` | はい | `guild_id`, `ics_uid` |

### 外部キー

外部キーはありません。

## `message_analysis_log`

Ollamaによるメッセージ解析結果を保存します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `message_id` | `bigint` | 不可 |  | 一意キー |  |  |
| 3 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 4 | `channel_id` | `bigint` | 不可 |  | 索引 |  |  |
| 5 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 6 | `model` | `varchar(100)` | 不可 |  |  |  |  |
| 7 | `aggression` | `int` | 不可 |  |  |  |  |
| 8 | `intimidation` | `int` | 不可 |  |  |  |  |
| 9 | `insult` | `int` | 不可 |  |  |  |  |
| 10 | `sarcasm` | `int` | 不可 |  |  |  |  |
| 11 | `snide` | `int` | 不可 |  |  |  |  |
| 12 | `discomfort` | `int` | 不可 |  |  |  |  |
| 13 | `max_score` | `int` | 不可 |  | 索引 |  |  |
| 14 | `reason` | `text` | 可 |  |  |  |  |
| 15 | `raw_result` | `text` | 可 |  |  |  |  |
| 16 | `should_react` | `tinyint(1)` | 不可 |  |  |  |  |
| 17 | `should_notify` | `tinyint(1)` | 不可 |  |  |  |  |
| 18 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `idx_message_analysis_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_message_analysis_max_score` | いいえ | `max_score`, `created_at` |
| `idx_message_analysis_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_analysis_log_channel_id` | いいえ | `channel_id` |
| `ix_message_analysis_log_guild_id` | いいえ | `guild_id` |
| `ix_message_analysis_log_user_id` | いいえ | `user_id` |
| `message_id` | はい | `message_id` |

### 外部キー

外部キーはありません。

## `message_delete_log`

Discordメッセージ削除ログを保存します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `message_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `guild_id` | `bigint` | 可 |  | 索引 |  |  |
| 4 | `channel_id` | `bigint` | 不可 |  | 索引 |  |  |
| 5 | `user_id` | `bigint` | 可 |  | 索引 |  |  |
| 6 | `content` | `text` | 可 |  |  |  |  |
| 7 | `bot_flg` | `tinyint(1)` | 可 |  |  |  |  |
| 8 | `has_attachments` | `tinyint(1)` | 可 |  |  |  |  |
| 9 | `has_embeds` | `tinyint(1)` | 可 |  |  |  |  |
| 10 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `idx_message_delete_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_message_delete_message_created` | いいえ | `message_id`, `created_at` |
| `idx_message_delete_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_delete_log_channel_id` | いいえ | `channel_id` |
| `ix_message_delete_log_guild_id` | いいえ | `guild_id` |
| `ix_message_delete_log_message_id` | いいえ | `message_id` |
| `ix_message_delete_log_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。

## `message_edit_log`

Discordメッセージ編集ログを保存します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `message_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 4 | `channel_id` | `bigint` | 不可 |  | 索引 |  |  |
| 5 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 6 | `before_content` | `text` | 可 |  |  |  |  |
| 7 | `after_content` | `text` | 可 |  |  |  |  |
| 8 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `idx_message_edit_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_message_edit_message_created` | いいえ | `message_id`, `created_at` |
| `idx_message_edit_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_edit_log_channel_id` | いいえ | `channel_id` |
| `ix_message_edit_log_guild_id` | いいえ | `guild_id` |
| `ix_message_edit_log_message_id` | いいえ | `message_id` |
| `ix_message_edit_log_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。

## `message_log`

Discordメッセージ投稿ログを保存します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `message_id` | `bigint` | 不可 |  | 一意キー |  |  |
| 3 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 4 | `channel_id` | `bigint` | 不可 |  | 索引 |  |  |
| 5 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 6 | `bot_flg` | `tinyint(1)` | 不可 |  |  |  |  |
| 7 | `content` | `text` | 可 |  |  |  |  |
| 8 | `has_attachments` | `tinyint(1)` | 不可 |  |  |  |  |
| 9 | `has_embeds` | `tinyint(1)` | 不可 |  |  |  |  |
| 10 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |
| 11 | `message_created_at` | `datetime` | 可 |  |  |  |  |
| 12 | `has_stickers` | `tinyint(1)` | 不可 | 0 |  |  |  |
| 13 | `stickers` | `text` | 可 |  |  |  |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `idx_channel_created` | いいえ | `channel_id`, `created_at` |
| `idx_user_created` | いいえ | `user_id`, `created_at` |
| `ix_message_log_channel_id` | いいえ | `channel_id` |
| `ix_message_log_guild_id` | いいえ | `guild_id` |
| `ix_message_log_user_id` | いいえ | `user_id` |
| `message_id` | はい | `message_id` |

### 外部キー

外部キーはありません。

## `niconico_info_event`

ニコニコインフォ通知対象記事と送信状態を管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `source_key` | `varchar(255)` | 不可 |  | 一意キー |  |  |
| 3 | `title` | `text` | 不可 |  |  |  |  |
| 4 | `start_date` | `date` | 可 |  |  |  |  |
| 5 | `end_date` | `date` | 可 |  |  |  |  |
| 6 | `date_text` | `text` | 可 |  |  |  |  |
| 7 | `explanation` | `text` | 可 |  |  |  |  |
| 8 | `link` | `text` | 可 |  |  |  |  |
| 9 | `organizer_user` | `text` | 可 |  |  |  |  |
| 10 | `organizer_link` | `text` | 可 |  |  |  |  |
| 11 | `categories` | `text` | 可 |  |  |  |  |
| 12 | `source_url` | `text` | 可 |  |  |  |  |
| 13 | `send_flg` | `tinyint(1)` | 不可 |  | 索引 |  |  |
| 14 | `delete_flg` | `tinyint(1)` | 不可 |  | 索引 |  |  |
| 15 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_niconico_info_event_delete_flg` | いいえ | `delete_flg` |
| `ix_niconico_info_event_send_flg` | いいえ | `send_flg` |
| `ix_niconico_info_event_source_key` | はい | `source_key` |

### 外部キー

外部キーはありません。

## `niconico_info_filter`

ニコニコインフォ通知フィルターを管理します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `mode` | `varchar(20)` | 不可 |  | 索引 |  |  |
| 4 | `keyword` | `text` | 不可 |  |  |  |  |
| 5 | `enabled` | `tinyint(1)` | 不可 |  | 索引 |  |  |
| 6 | `delete_flg` | `tinyint(1)` | 不可 |  | 索引 |  |  |
| 7 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `ix_niconico_info_filter_delete_flg` | いいえ | `delete_flg` |
| `ix_niconico_info_filter_enabled` | いいえ | `enabled` |
| `ix_niconico_info_filter_guild_id` | いいえ | `guild_id` |
| `ix_niconico_info_filter_mode` | いいえ | `mode` |

### 外部キー

外部キーはありません。

## `voice_status_log`

Discordボイス状態変更ログを保存します。

- ストレージエンジン: `InnoDB`
- 照合順序: `utf8mb4_0900_ai_ci`

### カラム定義

| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |
|---:|---|---|---|---|---|---|---|
| 1 | `id` | `int` | 不可 |  | 主キー | auto_increment |  |
| 2 | `before_guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 3 | `after_guild_id` | `bigint` | 不可 |  | 索引 |  |  |
| 4 | `user_id` | `bigint` | 不可 |  | 索引 |  |  |
| 5 | `before_channel_id` | `bigint` | 可 |  | 索引 |  |  |
| 6 | `after_channel_id` | `bigint` | 可 |  | 索引 |  |  |
| 7 | `before_mute` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 8 | `after_mute` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 9 | `before_deaf` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 10 | `after_deaf` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 11 | `before_video` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 12 | `after_video` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 13 | `before_stream` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 14 | `after_stream` | `tinyint(1)` | 可 |  | 索引 |  |  |
| 15 | `created_at` | `datetime` | 不可 | now() |  | DEFAULT_GENERATED |  |

### インデックス

| インデックス名 | 一意 | カラム |
|---|---|---|
| `PRIMARY` | はい | `id` |
| `idx_after_channel_created` | いいえ | `after_channel_id`, `created_at` |
| `idx_before_channel_created` | いいえ | `before_channel_id`, `created_at` |
| `idx_user_created` | いいえ | `user_id`, `created_at` |
| `ix_voice_status_log_after_channel_id` | いいえ | `after_channel_id` |
| `ix_voice_status_log_after_deaf` | いいえ | `after_deaf` |
| `ix_voice_status_log_after_guild_id` | いいえ | `after_guild_id` |
| `ix_voice_status_log_after_mute` | いいえ | `after_mute` |
| `ix_voice_status_log_after_stream` | いいえ | `after_stream` |
| `ix_voice_status_log_after_video` | いいえ | `after_video` |
| `ix_voice_status_log_before_channel_id` | いいえ | `before_channel_id` |
| `ix_voice_status_log_before_deaf` | いいえ | `before_deaf` |
| `ix_voice_status_log_before_guild_id` | いいえ | `before_guild_id` |
| `ix_voice_status_log_before_mute` | いいえ | `before_mute` |
| `ix_voice_status_log_before_stream` | いいえ | `before_stream` |
| `ix_voice_status_log_before_video` | いいえ | `before_video` |
| `ix_voice_status_log_user_id` | いいえ | `user_id` |

### 外部キー

外部キーはありません。
