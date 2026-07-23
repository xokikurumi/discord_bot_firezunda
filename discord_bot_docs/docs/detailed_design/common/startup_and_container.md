# 起動・DI・Cog 登録詳細

## 1. 目的

Bot プロセス起動時に、DB 初期化、Service 生成、Cog 登録、slash command 同期、Discord 接続開始、終了時の DB リソース解放を行う。

## 2. Bot 設定

| 項目 | 仕様 |
|---|---|
| command prefix | `!` |
| max messages | `10000` |
| intents | default に加えて `message_content`、`members`、`moderation`、`reactions`、`messages`、`voice_states` を有効化 |

## 3. 環境設定

起動前に Discord token が空の場合は `RuntimeError` を送出する。DB ホスト値が誤字 `localohst` の場合も `RuntimeError` を送出し、誤設定のまま起動しない。

## 4. 起動シーケンス

1. 非同期 main を開始する。
2. Discord token と DB host を検証する。
3. DB 初期化を実行する。
4. Container から Service インスタンスを生成する。
5. 各 Cog を Bot に登録する。
6. Bot を Discord token で開始する。
7. 終了時は async engine を dispose する。

## 5. DB 初期化呼び出し

DB 初期化では engine の begin ブロックを開き、ORM metadata の `create_all` を同期実行し、その後に軽量マイグレーションを実行する。完了時は `DB initialized.` を出力する。

## 6. Container

| Factory | 生成する Service | 依存 |
|---|---|---|
| `create_message_service` | MessageLogService | session factory |
| `create_voice_status_service` | VoiceChannelStatusService | session factory |
| `create_message_reaction_service` | MessageReactionService | session factory、bot |
| `create_message_watcher_service` | MessageWatcherService | session factory、bot |
| `create_dice_roll_service` | DiceRollService | なし |
| `create_p2pquake_service` | P2PQuakeService | bot、session factory |
| `create_ics_guild_event_service` | IcsGuildEventService | bot、session factory |
| `create_communication_trend_service` | CommunicationTrendService | bot、session factory |
| `create_niconico_user_video_service` | NiconicoUserVideoService | bot、session factory |
| `create_niconico_info_service` | NiconicoInfoService | bot、session factory |

## 7. Cog 登録順

Service を先にすべて生成し、次の順序で Cog を登録する。

| 順序 | Cog | 役割 |
|---:|---|---|
| 1 | MessageCog | メッセージ作成/編集/削除ログ |
| 2 | VoiceCog | ボイス状態ログ |
| 3 | MessageReactionCog | キーワードリアクション |
| 4 | MessageWatcherCog | Ollama 投稿分析 |
| 5 | AnalysisCog | 分析フィードバック管理 |
| 6 | DiceRollCog | ダイスロール |
| 7 | P2PQuakeCog | 災害通知 |
| 8 | IcsGuildEventCog | ICS 予定イベント取り込み |
| 9 | CommunicationTrendCog | 半期コミュニケーション分析 |
| 10 | NiconicoUserVideoCog | Niconico 投稿通知 |
| 11 | NiconicoInfoCog | Niconico Info 通知 |

## 8. slash command 同期

`on_ready` の初回実行時のみ slash command を同期する。
グローバル同期後、設定で guild 同期が有効な場合は、参加中の各 guild に global command を copy する。
その後 guild sync を実行する。guild 単位の同期失敗はログ出力に留め、他 guild の処理を継続する。

## 9. 終了処理

Bot 起動処理全体を `try/finally` で囲み、例外または通常終了のどちらでも engine dispose を実行する。KeyboardInterrupt は捕捉して停止メッセージを出力する。
