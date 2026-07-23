# Geolonia 住所同期詳細

## 1. 目的

Geolonia Japanese Addresses の住所データを DB に同期し、P2PQuake の観測点名から緯度経度を補完するための市区町村/町域データとして利用する。

## 2. 実行主体

住所同期は災害通知 Service の background task として起動する。
P2PQuake watcher 起動時に、JMA 震度観測点同期 task と並行して Geolonia 住所同期 task を開始する。
watcher 終了時に cancel する。

## 3. 設定

| 設定 | 用途 |
|---|---|
| `GEOLONIA_JAPANESE_ADDRESSES_API_BASE_URL` | API base URL |
| `GEOLONIA_ADDRESS_SYNC_ENABLED` | 同期有効/無効 |
| `GEOLONIA_ADDRESS_SYNC_CHECK_INTERVAL_SECONDS` | due 判定間隔 |

## 4. due 判定

同期 state 名は `geolonia_japanese_addresses` とする。最終同期日時がない場合は due。日時に timezone がなければ UTC とみなす。

最新の定期同期基準日は UTC の 1 月 1 日または 6 月 1 日とする。

| 現在日時 | 最新基準日 |
|---|---|
| 当年 1 月 1 日より前 | 前年 6 月 1 日 |
| 当年 1 月 1 日以上 6 月 1 日未満 | 当年 1 月 1 日 |
| 当年 6 月 1 日以上 | 当年 6 月 1 日 |

最終同期日時が最新基準日より古い場合に同期する。

## 5. 排他制御

同期本体は `asyncio.Lock` で囲む。Lock 取得後に再度 due 判定し、他 task による同期済みの場合は終了する。

## 6. 同期処理

1. 同期開始ログを出す。
2. 現在 UTC を `synced_at` とする。
3. `{base}.json` を取得し、都道府県ごとの市区町村一覧を得る。
4. 都道府県、市区町村ごとに `{base}/{pref}/{municipality}.json` を取得する。
5. 町域行を DB upsert 用 row に変換する。
6. row がある municipality ごとに bulk upsert する。
7. sync state に `synced_at` を保存する。
8. DB municipality cache、municipality-prefecture cache、town cache を破棄する。
9. 総 row 数付きで完了ログを出す。

## 7. row 変換

| DB 項目 | 値 |
|---|---|
| prefecture | `prefecture`、`pref`、引数 pref の順 |
| municipality | `city`、`municipality`、引数 municipality の順 |
| town | `town`、`area`、`name` の順 |
| lat | `lat` または `latitude` を float 化 |
| lng | `lng`、`lon`、`longitude` を float 化 |
| source_updated_at | synced_at |

lat/lng が数値化できない、または town が空の場合は除外する。

## 8. 座標補完での利用

P2PQuake の震度地点に緯度経度がない場合、観測点名から都道府県、市区町村、町域を推定する。DB 住所データは以下の順に利用する。

1. 観測点名に都道府県が含まれない場合、市区町村名から都道府県を逆引きする。ただし候補都道府県が 1 件のときのみ採用する。
2. 都道府県内の市区町村一覧から、観測点名に含まれる最長一致名を採用する。
3. 市区町村内の町域一覧から、観測点名に含まれる最長一致町域を採用する。
4. 町域が見つかれば町域座標を返す。
5. 町域が見つからなければ市区町村内の町域座標平均を代表点として返す。

市区町村抽出では都道府県名を先頭から除去し、最初に現れる `市`、`区`、`町`、`村` までを市区町村候補とする。

## 9. キャッシュ

DB から取得した市区町村一覧、町域一覧、市区町村から都道府県への逆引き map はメモリキャッシュする。住所同期完了時に全て破棄する。
