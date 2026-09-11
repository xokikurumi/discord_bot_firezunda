# P2PQuake 通知詳細

## 1. 目的

P2PQuake WebSocket から地震情報、津波予報、緊急地震速報を受信し、設定された Discord チャンネルへ通知する。地震/津波イベントは必要に応じて地図画像も生成して投稿する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| P2PQuakeCog | WebSocket watcher task、再起動制御、通知設定コマンドを提供する |
| P2PQuakeService | WebSocket 接続、イベント整形、通知、画像生成、JMA/Geolonia 同期を行う |
| NotifyChannelConfigRepository | `QUAKE` カテゴリ通知先を管理する |
| JmaShindoStationRepository | JMA 震度観測点を同期/検索する |
| GeoloniaAddressRepository | 住所データを同期/検索する |

## 3. 対象イベント

| code | 内容 |
|---:|---|
| 551 | 地震情報 |
| 552 | 津波予報 |
| 556 | 緊急地震速報 警報 |

上記以外の code は無視する。

## 4. watcher 起動と再起動

Cog load 時に watcher task を開始する。
task が予期せず終了した場合、unload 中、Bot close 済み、cancel 済みでなければ再起動する。
再起動は `P2PQUAKE_RECONNECT_DELAY` 秒後に行う。
Cog unload 時は watcher task と restart task を cancel する。

Service は機能が無効なら終了する。
有効なら Bot ready を待ち、JMA 観測点同期 task と Geolonia 住所同期 task を並行起動する。
その後 WebSocket を監視する。watcher 終了時は同期 task を cancel する。

## 5. WebSocket 受信

`aiohttp.ClientSession` を total timeout なし、connect timeout 30 秒、heartbeat 30 秒で作成する。
WebSocket に接続し、TEXT message は JSON parse して処理する。
WS error は例外として再接続ループに戻す。

## 6. 重複抑止

event id は `id`、`_id` の順に取得して文字列化する。id があり、直近 seen list に存在する場合は無視する。新規 id は seen list に追加し、最大 200 件を超えた場合は末尾 200 件だけ残す。

## 7. 通知しきい値

code 551 と 556 は最大震度が `P2PQUAKE_MIN_NOTIFY_SCALE` 未満なら通知しない。
最大震度は earthquake.maxScale、points、areas の scale/scaleFrom/scaleTo を整数化し最大値を取る。
最大震度が取得できない場合は、最小通知震度が 10 以下なら通知対象とする。
津波 code 552 は震度しきい値対象外。

## 8. 通知本文

### 地震情報

発表時刻、発生時刻、震源地、規模/深さ、最大震度、津波有無、各地の震度を含める。各地の震度は震度降順で `- 地点名: 震度` とする。

### 津波予報

発表時刻、解除状態、areas ごとの地域名、警報等級、到達予想、最大高さを含める。

### 緊急地震速報

発表時刻、発生時刻、震源地、規模/深さ、最大予測震度、areas ごとの地域名と予測震度を含める。

## 9. 表示変換

| 値 | 変換 |
|---|---|
| 深さ null/-1 | `-` |
| 深さ 0 | `ごく浅い` |
| 深さ その他 | `{depth}km` |
| 震度 10/20/30/40/45/50/55/60/70 | `1/2/3/4/5弱/5強/6弱/6強/7` |
| 津波 `None` | `なし` |
| 津波 `Unknown` | `不明` |
| 津波 `Checking` | `調査中` |
| 津波 `NonEffective` | `若干の海面変動` |
| 津波 `Watch` | `津波注意報` |
| 津波 `Warning` | `津波警報以上` |
| 津波等級 `MajorWarning` | `大津波警報` |
| 津波等級 `Warning` | `津波警報` |
| 津波等級 `Watch` | `津波注意報` |
| 津波等級 `Yoho` | `津波予報` |

## 10. Discord 送信

全 guild について `QUAKE` カテゴリの有効通知設定を取得する。
channel が Bot cache にない場合は warning を出して skip。
本文は mention を prefix とし、1900 文字以内に分割して送信する。
長い 1 行は 1900 文字単位で分割する。

送信対象 channel が 1 つ以上ある場合、code 552 で津波 area があれば津波画像 task、そうでなく地震画像データがあれば震源/震度画像 task を background で起動する。

## 11. JMA 震度観測点同期

設定が無効なら終了する。
有効なら `JMA_SHINDO_STATION_SYNC_CHECK_INTERVAL_SECONDS` ごとに due 判定する。
最終同期がない、または最終同期から設定日数以上経過した場合に同期する。
同期は lock で排他し、JMA HTML の table から `震度観測点名称` と `緯度(度)` を含む表を探す。

row は region、station、address、緯度度/分、経度度/分、観測開始/終了を変換する。
source updated at も保存する。緯度経度は度 + 分/60。
変換不能 row は除外する。同期後は DB upsert、sync state 更新、station cache 破棄を行う。

## 12. 震度地点座標解決

震度地点は、API の latitude/longitude があればそれを使う。
ない場合は DB の JMA 観測点名一致、DB の Geolonia 住所、都道府県代表座標の順に補完する。
同一地点 key では最大震度の row を残し、震度降順に並べる。

観測点名正規化では `（旧）`、`(旧)`、`（臨時）`、`(臨時)`、半角/全角空白を削除する。

## 13. 地震画像

震源座標または震度地点がある場合に PNG を生成する。
サイズは 1080x760、地図領域は左 42、上 54、幅 790、高さ 540。
背景は GSI blank tile を Web Mercator で取得/キャッシュして貼り合わせる。
震度地点は震度色の円、震源は赤い `×` で描画する。
右側に震源地、発生時刻、緯度、経度、規模、深さ、最大震度、震度凡例を描く。

震度地点の画像表示は次の通り整理する。

| 項目 | 内容 |
|---|---|
| 通常時の最小表示震度 | 震度 3 |
| 高密度判定 | 震度 3 以上の表示候補が 50 件を超える |
| 高密度時の最小表示震度 | 震度 4 |
| 除外条件 | 正規化後震度がない、または最小表示震度未満 |
| 凡例 | 最小表示震度以上の震度だけを表示する |

震度点は震度降順で抽出し、描画時は逆順に処理する。
これにより低い震度の点を先に描き、高い震度の点を上に重ねる。
震度 5 弱以上の点は半径を大きくし、震度 5 強以上の円内ラベルは白文字、それ未満は濃色文字にする。

## 14. 津波画像

津波 area がある場合に PNG を生成する。サイズと地図領域は地震画像と同じ。津波予報区名を代表座標へ変換し、等級色の円と短縮ラベルを描く。右側に発表時刻、対象区域数、解除状態、凡例、区域サマリを描く。

## 15. GSI tile cache

tile path は `{GSI_TILE_CACHE_DIR}/{zoom}/{x}/{y}.png`。
存在する場合は読み込む。
存在しない場合は `{GSI_BLANK_TILE_BASE_URL}/{zoom}/{x}/{y}.png` から取得する。
保存できる場合は cache に保存する。取得/保存失敗は warning で継続する。

## 16. Font

設定 font path を最優先し、Linux と Windows の代表的な日本語 font path を順に試す。全て失敗した場合は Pillow default font を使い warning を出す。
