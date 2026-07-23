# ボイス状態ログ詳細

## 1. 目的

Discord のボイス状態変更イベントを保存し、入退室、移動、ミュート、スピーカーミュート、カメラ、配信状態の変化を時系列で追跡できるようにする。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| VoiceCog | `on_voice_state_update` listener を提供する |
| VoiceChannelStatusService | before/after の状態を DB 行へ変換する |
| VoiceChannelStatusRepository | `voice_status_log` へ insert する |

## 3. イベント処理

1. `on_voice_state_update(member, before, after)` が発火する。
2. Service の `log_status` を呼び出す。
3. before/after の channel が null の場合は guild/channel id を `0` として扱う。
4. member id と voice state の self flags を保存する。
5. 例外はログ出力して Bot を継続する。

## 4. 保存項目

| 項目 | 値 |
|---|---|
| before_guild_id | before.channel.guild.id、before.channel がなければ 0 |
| after_guild_id | after.channel.guild.id、after.channel がなければ 0 |
| user_id | member.id |
| before_channel_id | before.channel.id、before.channel がなければ 0 |
| after_channel_id | after.channel.id、after.channel がなければ 0 |
| before_mute / after_mute | before/after.self_mute |
| before_deaf / after_deaf | before/after.self_deaf |
| before_video / after_video | before/after.self_video |
| before_stream / after_stream | before/after.self_stream |

## 5. 再実装メモ

ボイス状態は全変更を記録する。入退室だけに限定せず、同じ channel 内の self mute 変更なども insert 対象にする。
