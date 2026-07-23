# Niconico Info 確認・通知

## 1. 基本情報

| 項目 | 内容 |
|---|---|
| バッチ ID | BATCH-006 |
| 処理名 | Niconico Info 確認・通知 |
| 実装 | `cogs/tasks/niconico_info_cog.py`、`services/task/niconico_info_service.py` |
| 実行方式 | 定期処理・手動実行 |
| 手動コマンド | `!niconico_info_check`、`/niconico_info_check` |

## 2. 処理概要

設定された Niconico Info のカテゴリページを巡回し、新規記事を検出して Discord へ通知します。

## 3. 実行条件

| 項目 | 内容 |
|---|---|
| 有効化設定 | `NICONICO_INFO_ENABLED=true` |
| チェック間隔 | `NICONICO_INFO_CHECK_INTERVAL_SECONDS` 秒 |
| 対象 URL | `NICONICO_INFO_TARGET_URLS` |
| 通知カテゴリ | `NICONICO_INFO` |

## 4. 処理詳細

1. 対象 URL の HTML を取得する。
2. 記事一覧またはイベントカードを解析する。
3. title、期間、説明、リンク、カテゴリなどから `source_key` を生成する。
4. 未登録の `source_key` を `niconico_info_event` に保存する。
5. 未送信 row を取得する。
6. サーバー別通知先とフィルターを取得する。
7. exclude フィルター、include フィルターを判定する。
8. 通知本文を生成し、Discord へ送信する。
9. 通知済み row を送信済みに更新する。

## 5. 入出力

| 種別 | 内容 |
|---|---|
| 入力 | Niconico Info HTML |
| 参照 | `b_notify_cannel_config`、`niconico_info_filter` |
| 出力 | `niconico_info_event`、Discord 通知 |

## 6. 異常時の確認

| 症状 | 確認内容 |
|---|---|
| 新規記事が検出されない | 対象 URL と HTML 構造変更を確認する |
| 通知されない | `NICONICO_INFO` 通知先と filter 条件を確認する |
| 同じ記事が重複する | `source_key` の生成条件を確認する |
