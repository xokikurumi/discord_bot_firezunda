import re
from common import db
from common import ollama
# pip install Requests
import requests
# pip install beautifulsoup4
from bs4 import BeautifulSoup

MENTENANCE_URL = "https://blog.nicovideo.jp/niconews/category/ge_maintenance/"
VOICEROID_URL = "https://blog.nicovideo.jp/niconews/category/ge_user/"
INFO_SELECTOR = " "
def GetMaintenance():
	result = []
	# ニコニコインフォにアクセス
	query = "SELECT id, link, title, body FROM browser_send WHERE send = 0 AND category = 'nicoCH'";
	sqlResult = db.select(query)
	for row in sqlResult:
		resultClient = {
			"link": row[1],
			"title": row[2],
			"body": row[3]
		}
		db.insert("UPDATE browser_send SET send = 1 WHERE id = " + str(row[0]))
		result.append(resultClient)

	return result

		
def GetVOICEROID():
	result = []
	# ニコニコインフォにアクセス
	query = "SELECT id, link, title, body FROM browser_send WHERE send = 0 AND category = 'vocaloid'";
	sqlResult = db.select(query)
	for row in sqlResult:
		resultClient = {
			"link": row[1],
			"title": row[2],
			"body": row[3]
		}
		db.insert("UPDATE browser_send SET send = 1 WHERE id = " + str(row[0]))
		result.append(resultClient)

	return result
# def GetUserVideos(userid):

