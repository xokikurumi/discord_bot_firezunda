<!--
このファイルは Discord bot の SQLAlchemy モデル定義から生成したテーブル定義書です。
ドキュメントは Markdown / UTF-8 で保存しています。
-->
# テーブル定義書

- 生成日時: 2026-07-14 08:22:31
- 文字コード: UTF-8

## 一覧

| テーブル名 | 分類 | 説明 |
|---|---|---|
| [`b_geolonia_address`](tables/b_geolonia_address.md) | 基礎データ・設定 | Geolonia住所データ。住所から緯度・経度を解決するために使用します。 |
| [`b_geolonia_sync_state`](tables/b_geolonia_sync_state.md) | 基礎データ・設定 | Geolonia住所データ同期状態を管理します。 |
| [`b_jma_shindo_station`](tables/b_jma_shindo_station.md) | 基礎データ・設定 | 気象庁震度観測点データ。観測地点の住所・緯度・経度を管理します。 |
| [`b_jma_sync_state`](tables/b_jma_sync_state.md) | 基礎データ・設定 | 気象庁震度観測点データ同期状態を管理します。 |
| [`b_m_niconico_video_infomation`](tables/b_m_niconico_video_infomation.md) | タスク・通知 | ニコニコ動画ユーザー投稿通知の監視対象ユーザーを管理します。 |
| [`b_niconico_notify_cannel_config`](tables/b_niconico_notify_cannel_config.md) | タスク・通知 | ニコニコ動画ユーザーごとの通知先チャンネル設定を管理します。 |
| [`b_niconico_video_send_log`](tables/b_niconico_video_send_log.md) | タスク・通知 | ニコニコ動画ユーザー投稿通知の検出結果と送信済み状態を管理します。 |
| [`b_notify_cannel_config`](tables/b_notify_cannel_config.md) | 基礎データ・設定 | 通知カテゴリごとの通知先チャンネル設定を管理します。 |
| [`b_reaction_keywords`](tables/b_reaction_keywords.md) | 基礎データ・設定 | キーワードに応じた自動リアクション設定を管理します。 |
| [`communication_trend_analysis`](tables/communication_trend_analysis.md) | ログ | 半期ごとのコミュニケーション傾向分析結果を保存します。 |
| [`ics_guild_event_config`](tables/ics_guild_event_config.md) | タスク・通知 | ICS予定イベント取り込みのギルド別有効・無効設定を管理します。 |
| [`ics_guild_event_import`](tables/ics_guild_event_import.md) | タスク・通知 | ICS予定イベントの取り込み済み状態を管理します。 |
| [`message_analysis_feedback`](tables/message_analysis_feedback.md) | ログ | Ollamaメッセージ分析に対する管理者フィードバックを保存します。 |
| [`message_analysis_log`](tables/message_analysis_log.md) | ログ | Ollamaによるメッセージ解析結果を保存します。 |
| [`message_delete_log`](tables/message_delete_log.md) | ログ | Discordメッセージ削除ログを保存します。 |
| [`message_edit_log`](tables/message_edit_log.md) | ログ | Discordメッセージ編集ログを保存します。 |
| [`message_log`](tables/message_log.md) | ログ | Discordメッセージ投稿ログを保存します。 |
| [`niconico_info_event`](tables/niconico_info_event.md) | タスク・通知 | ニコニコインフォ通知対象記事と送信状態を管理します。 |
| [`niconico_info_filter`](tables/niconico_info_filter.md) | タスク・通知 | ニコニコインフォ通知フィルターを管理します。 |
| [`voice_status_log`](tables/voice_status_log.md) | ログ | Discordボイスチャンネル状態変更ログを保存します。 |

## 分類別

### ログ

- [`communication_trend_analysis`](tables/communication_trend_analysis.md)
- [`message_analysis_feedback`](tables/message_analysis_feedback.md)
- [`message_analysis_log`](tables/message_analysis_log.md)
- [`message_delete_log`](tables/message_delete_log.md)
- [`message_edit_log`](tables/message_edit_log.md)
- [`message_log`](tables/message_log.md)
- [`voice_status_log`](tables/voice_status_log.md)

### タスク・通知

- [`b_m_niconico_video_infomation`](tables/b_m_niconico_video_infomation.md)
- [`b_niconico_notify_cannel_config`](tables/b_niconico_notify_cannel_config.md)
- [`b_niconico_video_send_log`](tables/b_niconico_video_send_log.md)
- [`ics_guild_event_config`](tables/ics_guild_event_config.md)
- [`ics_guild_event_import`](tables/ics_guild_event_import.md)
- [`niconico_info_event`](tables/niconico_info_event.md)
- [`niconico_info_filter`](tables/niconico_info_filter.md)

### 基礎データ・設定

- [`b_geolonia_address`](tables/b_geolonia_address.md)
- [`b_geolonia_sync_state`](tables/b_geolonia_sync_state.md)
- [`b_jma_shindo_station`](tables/b_jma_shindo_station.md)
- [`b_jma_sync_state`](tables/b_jma_sync_state.md)
- [`b_notify_cannel_config`](tables/b_notify_cannel_config.md)
- [`b_reaction_keywords`](tables/b_reaction_keywords.md)
