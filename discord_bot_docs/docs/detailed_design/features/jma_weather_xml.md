# 気象庁防災気象情報 XML 通知詳細

!!! warning "現行ソース未確認"
    `D:\6000.PROJECTS\discord_bot_firezunda\discord_bot_src` の現行ローカルソースには、
    本機能の Cog、Service、Repository、Model、設定値が存在しない。
    この文書は過去実装または検討内容として残しているため、現行実装の設計書として扱わない。

## 1. 目的

気象庁の高頻度防災気象情報 Atom feed を定期確認し、警報・注意報系 XML を検出する。
新規イベントを保存し、通知カテゴリ `WEATHER_WARNING` に設定された Discord チャンネルへ通知する。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| JmaWeatherXmlCog | 定期確認 task の起動/停止、手動確認コマンドを提供する |
| JmaWeatherXmlService | Atom feed 取得、XML 詳細取得、保存、未送信通知、本文整形を行う |
| JmaWeatherXmlEventRepository | 検出イベントの重複確認、追加、未送信取得、送信済み更新を行う |
| NotifyChannelConfigRepository | `WEATHER_WARNING` カテゴリの通知先を取得する |

## 3. 設定

| 設定 | 用途 |
|---|---|
| `JMA_WEATHER_XML_ENABLED` | 定期確認を有効化する |
| `JMA_WEATHER_XML_FEED_URL` | 高頻度防災気象情報 Atom feed URL |
| `JMA_WEATHER_XML_CHECK_INTERVAL_SECONDS` | 定期確認間隔 |
| `JMA_WEATHER_XML_TIMEOUT_SECONDS` | feed/XML 取得 timeout |
| `JMA_WEATHER_XML_MAX_ENTRIES` | 1 回の feed 確認で見る entry 上限 |
| `JMA_WEATHER_XML_NOTIFY_ON_STARTUP` | 起動直後に既存 feed entry を通知対象にするか |
| `JMA_WEATHER_XML_NOTIFY_ADVISORIES` | 注意報のみの XML も通知対象にするか |
| `JMA_WEATHER_XML_TARGET_TITLE_KEYWORDS` | 対象 title 判定用 keyword |

## 4. Cog 動作

Cog load 時に定期確認 task が存在しない、または完了済みなら新規 task を作成する。
Cog unload 時は task があれば cancel する。

手動コマンド `jma_weather_xml_check` は guild 限定、管理者限定とする。
実行時は開始メッセージを送信し、1 回分の確認処理を実行し、終了メッセージを送信する。
管理者権限がない場合は権限エラーを Discord 応答へ変換する。

## 5. 定期確認

機能が無効なら初期ログを出力して終了する。
有効なら Bot ready を待ち、Bot close まで次の処理を繰り返す。

1. 1 回分の確認処理を実行する。
2. 設定された確認間隔だけ sleep する。

1 回分の確認処理では、検出処理、未送信通知処理の順に実行する。
例外はログ出力し、定期確認 task 全体は継続する。

## 6. feed 取得

feed 取得はブロッキング HTTP のため別 thread で実行する。
HTTP request には専用 User-Agent を設定し、timeout は設定値を使う。
レスポンス本文は UTF-8 として decode し、XML として parse する。

Atom entry は先頭から最大 `JMA_WEATHER_XML_MAX_ENTRIES` 件だけ確認する。
entry title が対象 keyword に一致しない場合は除外する。
keyword が空の場合は、title に `警報` と `注意報` の両方を含む entry を対象にする。

対象 entry から次の値を抽出する。

| 項目 | 抽出元 |
|---|---|
| title | entry の title |
| author | entry 配下の最初の name |
| content | entry の content |
| updated_at | entry の updated |
| link | link 要素の href、なければ id |

`updated_at` は ISO-8601 として parse し、`Z` は UTC offset として扱う。
parse できない場合は null とする。

## 7. 重複キー

source key は author、updated_at、正規化 content を `|` で連結し、UTF-8 SHA-256 hex digest にする。
content 正規化では連続空白を 1 文字の空白にし、前後空白を除去する。

同じ source key かつ削除フラグ false の行が既に存在する場合、新規保存しない。

## 8. XML 詳細取得

起動直後の既存 entry を通知しない設定の場合、初回確認では詳細 XML を取得せず保存だけ行う。
それ以外で link がある場合は XML 詳細を取得し、通知用項目を補完する。

XML 詳細取得に失敗した場合は警告ログを出し、Atom entry 由来の値のまま処理を継続する。

XML 詳細から次を抽出する。

| 項目 | 抽出元 |
|---|---|
| report title | 最初の Title |
| info type | 最初の InfoType |
| headline | 最初の Text。空なら Atom content |
| area text | Warning/Item/Area/Name の一覧 |
| kind text | Warning/Item/Kind の Name と Status の一覧 |

Warning type に `市町村等` を含むものは summary 対象外とする。
area と kind は重複を除外し、各 12 件まで保存する。

## 9. 通知対象判定

`JMA_WEATHER_XML_NOTIFY_ADVISORIES` が true の場合は、検出した対象 entry をすべて通知対象にする。
false の場合は、kind text に注意報ではない警報名を含む場合だけ通知対象にする。

警報判定では kind label の `(` より前を名称として扱う。
名称に `警報` を含み、かつ `注意報` を含まない場合に警報ありとする。

## 10. 保存

新規 entry は `jma_weather_xml_event` に保存する。

| 項目 | 値 |
|---|---|
| source_key | 重複キー |
| title | Atom title |
| report_title | XML Title。未取得時は Atom title |
| info_type | XML InfoType |
| author | Atom author |
| headline | XML Text または Atom content |
| content | Atom content |
| area_text | 抽出 area のカンマ区切り |
| kind_text | 抽出 kind のカンマ区切り |
| link | XML URL |
| updated_at | Atom updated |
| send_flg | 通知不要または初回通知抑止なら true、通知対象なら false |
| delete_flg | false |

保存後は `initial_poll_done` を true にする。

## 11. 未送信通知

未送信取得では `send_flg=false`、`delete_flg=false` の行を id 昇順で最大 20 件取得する。
各行を通知処理した後、行 id を指定して `send_flg=true` に更新する。

通知処理中に一部チャンネル送信が失敗しても、エラーをログ出力して他チャンネルの処理を継続する。
未送信行単位の通知処理が戻った後は送信済みとして扱う。

## 12. Discord 通知

全 guild に対して、通知カテゴリ `WEATHER_WARNING` の有効な通知設定を取得する。
Bot cache から channel を取得できない場合は警告ログを出して skip する。

通知 message は通知設定の mention と本文を結合して作成する。
送信時は Discord message 上限を考慮し、先頭 1900 文字だけ送信する。

mention は次の規則で構築する。

| DB 値 | 出力 |
|---|---|
| 空 | 空文字 |
| `everyone` | `@everyone` |
| `here` | `@here` |
| `<@` で始まる値 | そのまま |
| 数字のみ | role mention |
| その他 | そのまま |

## 13. 通知本文

通知本文は次の順序で構成する。

1. `## 気象庁 防災気象情報`
2. report title または title を太字にした行
3. info type があれば種別行
4. author があれば発表行
5. updated_at があれば `yyyy/mm/dd hh:mm` 形式の更新行
6. kind text があれば警報・注意報行
7. area text があれば対象地域行
8. headline または content があれば空行を挟んで正規化本文
9. link があれば空行を挟んで URL

注意報通知が無効な場合、kind text の見出しは `警報` とする。
有効な場合は `警報・注意報` とする。

## 14. XML helper

XML 名前空間に依存しないよう、tag は `}` より後ろの local name で比較する。
直接子要素取得、子要素 text 取得、最初の子孫 text 取得、子孫一覧取得は local name で行う。
text 取得時は通知本文と重複キーで同じ正規化を行う。
