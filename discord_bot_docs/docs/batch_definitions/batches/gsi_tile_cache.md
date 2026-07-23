# GSI タイル事前キャッシュ

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-009 |
| 処理名 | GSI タイル事前キャッシュ |
| 実装 | `deploy/scripts/cache_gsi_tiles.py` |
| 実行方式 | 手動スクリプト |
| 起動契機 | 運用者実行 |

## 2. 処理概要

P2PQuake の地図画像生成で利用する国土地理院の blank tile を事前にローカルへ保存します。

## 3. 実行例

```bash
cd /opt/discord/current
sudo -u discord-bot .venv/bin/python deploy/scripts/cache_gsi_tiles.py --dry-run
sudo -u discord-bot .venv/bin/python deploy/scripts/cache_gsi_tiles.py
```

保存先を明示する場合の例です。

```bash
sudo -u discord-bot .venv/bin/python deploy/scripts/cache_gsi_tiles.py \
  --cache-dir /opt/discord/current/cache/gsi_tiles \
  --zoom 5 6 7
```

## 4. 主な引数

| 引数 | 内容 |
|---|---|
| `--cache-dir` | 保存先ディレクトリ |
| `--base-url` | GSI tile base URL |
| `--zoom` | 取得する zoom level |
| `--lat-min`、`--lat-max` | 緯度範囲 |
| `--lon-min`、`--lon-max` | 経度範囲 |
| `--force` | 既存ファイルも再取得する |
| `--dry-run` | 対象件数のみ表示する |

## 5. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | GSI blank tile |
| 出力 | `cache/gsi_tiles/<zoom>/<x>/<y>.png` |

## 6. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 取得に失敗する | ネットワーク、base URL、timeout を確認する |
| 画像生成時に tile がない | `GSI_TILE_CACHE_DIR` と cache 実体の場所を確認する |
