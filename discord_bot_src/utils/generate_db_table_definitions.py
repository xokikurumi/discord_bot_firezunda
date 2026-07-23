from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys

import pymysql

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config


TABLE_DESCRIPTIONS = {
	"b_geolonia_address": "Geolonia住所データ。地震観測地点などの住所から緯度経度を検索するために使用します。",
	"b_geolonia_sync_state": "Geolonia住所データの同期状態を管理します。",
	"b_jma_shindo_station": "気象庁震度観測点データ。観測地点の緯度経度検索に使用します。",
	"b_jma_sync_state": "気象庁震度観測点データの同期状態を管理します。",
	"b_m_niconico_video_infomation": "ニコニコ動画ユーザ投稿通知の監視対象ユーザを管理します。",
	"b_niconico_notify_cannel_config": "ニコニコ動画ユーザごとの通知先チャンネル設定を管理します。",
	"b_niconico_video_send_log": "ニコニコ動画ユーザ投稿通知の検出結果と送信済み状態を管理します。",
	"b_notify_cannel_config": "汎用通知カテゴリごとの通知先チャンネル設定を管理します。",
	"b_reaction_keywords": "キーワードに応じた自動リアクション設定を管理します。",
	"communication_trend_analysis": "半期ごとのコミュニケーション傾向分析結果を保存します。",
	"ics_guild_event_config": "ICS予定イベント取り込みのギルド別有効/無効設定を管理します。",
	"ics_guild_event_import": "ICS予定イベントの取り込み済み状態を管理します。",
	"message_analysis_log": "Ollamaによるメッセージ解析結果を保存します。",
	"message_delete_log": "Discordメッセージ削除ログを保存します。",
	"message_edit_log": "Discordメッセージ編集ログを保存します。",
	"message_log": "Discordメッセージ投稿ログを保存します。",
	"niconico_info_event": "ニコニコインフォ通知対象記事と送信状態を管理します。",
	"niconico_info_filter": "ニコニコインフォ通知フィルターを管理します。",
	"voice_status_log": "Discordボイス状態変更ログを保存します。",
}

KEY_DESCRIPTIONS = {
	"PRI": "主キー",
	"UNI": "一意キー",
	"MUL": "索引",
	"": "",
	None: "",
}


def fetch_schema():
	"""Fetch table, column, index, and foreign-key metadata from the current DB."""
	conn = pymysql.connect(
		host=config.DB_HOST,
		port=int(config.DB_PORT),
		user=config.DB_USER,
		password=config.DB_PASSWORD,
		database=config.DB_NAME,
		charset="utf8mb4",
		cursorclass=pymysql.cursors.DictCursor,
	)
	try:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT TABLE_NAME, TABLE_COMMENT, ENGINE, TABLE_COLLATION
				FROM INFORMATION_SCHEMA.TABLES
				WHERE TABLE_SCHEMA = %s
				ORDER BY TABLE_NAME
				""",
				(config.DB_NAME,),
			)
			tables = cur.fetchall()

			cur.execute(
				"""
				SELECT TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE,
					   IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA, COLUMN_COMMENT
				FROM INFORMATION_SCHEMA.COLUMNS
				WHERE TABLE_SCHEMA = %s
				ORDER BY TABLE_NAME, ORDINAL_POSITION
				""",
				(config.DB_NAME,),
			)
			columns = cur.fetchall()

			cur.execute(
				"""
				SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME
				FROM INFORMATION_SCHEMA.STATISTICS
				WHERE TABLE_SCHEMA = %s
				ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
				""",
				(config.DB_NAME,),
			)
			indexes = cur.fetchall()

			cur.execute(
				"""
				SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME,
					   REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
				FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
				WHERE TABLE_SCHEMA = %s
				  AND REFERENCED_TABLE_NAME IS NOT NULL
				ORDER BY TABLE_NAME, CONSTRAINT_NAME, ORDINAL_POSITION
				""",
				(config.DB_NAME,),
			)
			foreign_keys = cur.fetchall()
	finally:
		conn.close()

	return tables, columns, indexes, foreign_keys


def escape(value):
	"""Escape Markdown table separators and normalize None."""
	if value is None:
		return ""
	return str(value).replace("|", "\\|").replace("\n", "<br>")


def build_markdown(tables, columns, indexes, foreign_keys):
	"""Build the Markdown table definition document."""
	columns_by_table = defaultdict(list)
	for row in columns:
		columns_by_table[row["TABLE_NAME"]].append(row)

	index_parts = defaultdict(lambda: defaultdict(list))
	index_unique = defaultdict(dict)
	for row in indexes:
		table = row["TABLE_NAME"]
		name = row["INDEX_NAME"]
		index_parts[table][name].append(row["COLUMN_NAME"])
		index_unique[table][name] = row["NON_UNIQUE"] == 0

	fks_by_table = defaultdict(list)
	for row in foreign_keys:
		fks_by_table[row["TABLE_NAME"]].append(row)

	lines = [
		"# DBテーブル定義書",
		"",
		f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
		"文字コード: UTF-8",
		f"対象DB: `{config.DB_NAME}`",
		"",
		"## テーブル一覧",
		"",
	]

	for table in tables:
		table_name = table["TABLE_NAME"]
		description = TABLE_DESCRIPTIONS.get(table_name) or table.get("TABLE_COMMENT") or ""
		lines.append(f"- `{table_name}`: {description}")
	lines.append("")

	for table in tables:
		table_name = table["TABLE_NAME"]
		lines.append(f"## `{table_name}`")
		lines.append("")
		description = TABLE_DESCRIPTIONS.get(table_name) or table.get("TABLE_COMMENT") or ""
		if description:
			lines.append(description)
			lines.append("")
		lines.append(f"- ストレージエンジン: `{table.get('ENGINE') or ''}`")
		lines.append(f"- 照合順序: `{table.get('TABLE_COLLATION') or ''}`")
		lines.append("")
		lines.append("### カラム定義")
		lines.append("")
		lines.append("| No | カラム名 | データ型 | NULL許可 | デフォルト | キー | 追加属性 | コメント |")
		lines.append("|---:|---|---|---|---|---|---|---|")

		for col in columns_by_table[table_name]:
			key = KEY_DESCRIPTIONS.get(col["COLUMN_KEY"], col["COLUMN_KEY"] or "")
			lines.append(
				"| {no} | `{name}` | `{ctype}` | {nullable} | {default} | {key} | {extra} | {comment} |".format(
					no=col["ORDINAL_POSITION"],
					name=col["COLUMN_NAME"],
					ctype=col["COLUMN_TYPE"],
					nullable="可" if col["IS_NULLABLE"] == "YES" else "不可",
					default=escape(col["COLUMN_DEFAULT"]),
					key=escape(key),
					extra=escape(col["EXTRA"]),
					comment=escape(col.get("COLUMN_COMMENT") or ""),
				)
			)
		lines.append("")

		lines.append("### インデックス")
		lines.append("")
		if index_parts[table_name]:
			lines.append("| インデックス名 | 一意 | カラム |")
			lines.append("|---|---|---|")
			for index_name in sorted(index_parts[table_name].keys()):
				unique = "はい" if index_unique[table_name][index_name] else "いいえ"
				column_text = ", ".join(f"`{column}`" for column in index_parts[table_name][index_name])
				lines.append(f"| `{index_name}` | {unique} | {column_text} |")
		else:
			lines.append("インデックスはありません。")
		lines.append("")

		lines.append("### 外部キー")
		lines.append("")
		if fks_by_table[table_name]:
			lines.append("| 制約名 | カラム | 参照先 |")
			lines.append("|---|---|---|")
			for fk in fks_by_table[table_name]:
				lines.append(
					f"| `{fk['CONSTRAINT_NAME']}` | `{fk['COLUMN_NAME']}` | "
					f"`{fk['REFERENCED_TABLE_NAME']}`.`{fk['REFERENCED_COLUMN_NAME']}` |"
				)
		else:
			lines.append("外部キーはありません。")
		lines.append("")

	return "\n".join(lines)


def main():
	"""Generate DB_TABLE_DEFINITIONS.md from the current database schema."""
	tables, columns, indexes, foreign_keys = fetch_schema()
	markdown = build_markdown(tables, columns, indexes, foreign_keys)
	Path("DB_TABLE_DEFINITIONS.md").write_text(markdown, encoding="utf-8", newline="\n")
	print("DB_TABLE_DEFINITIONS.md をUTF-8で生成しました。")


if __name__ == "__main__":
	main()
