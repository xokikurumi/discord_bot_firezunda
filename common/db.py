import mysql.connector
from common import setting

def select(query):

	# MySQLに接続
	conn = mysql.connector.connect(
		host=setting.DATABASE_HOST,
		port=setting.DATABASE_PORT,
		user=setting.DATABASE_USER,
		password=setting.DATABASE_PASS,
		database=setting.DATABASE_DATABASE
	)
	# カーソルを取得
	cursor = conn.cursor()

	# データベース作成
	cursor.execute(query)
	result = cursor.fetchall()


	# 接続を閉じる
	cursor.close()
	conn.close()

	return result

def insert(query):

	# MySQLに接続
	conn = mysql.connector.connect(
		host=setting.DATABASE_HOST,
		port=setting.DATABASE_PORT,
		user=setting.DATABASE_USER,
		password=setting.DATABASE_PASS,
		database=setting.DATABASE_DATABASE
	)

	# カーソルを取得
	cursor = conn.cursor()

	# データベース作成
	result = cursor.execute(query)

	# 接続を閉じる
	cursor.close()
	conn.commit()
	conn.close()