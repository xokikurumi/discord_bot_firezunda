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
	response = requests.get(MENTENANCE_URL)
	response.encoding = response.apparent_encoding
	soup = BeautifulSoup(response.text, "html.parser")
	# 指定の領域の情報を取得
	articles = soup.select("ul#vp_1.l-main.l-main-list2 li.l-main.l-main-list2-item a")

	query = "SELECT link, title FROM niconico_links WHERE delete_flg = 0"
	dbResult = db.select(query)
	for article in articles:
		# タイトルとリンクを取得
		title = article.text.strip()
		link = article['href']
		
		# リンクから過去に取得済みのデータを除外する
		checked = False
		for rowData in dbResult:

			if rowData[0] == link:
				checked = True

		#print(checked)
		if checked == False:
			# DBに保存
			query = "INSERT INTO niconico_links( link, title )VALUES( '" + link + "', '" + title + "' )"
			db.insert(query)


			# 該当の記事の内容を取得
			rowResult = {'title' : title, 'content': '', 'summary': '', 'link': "https://blog.nicovideo.jp" + link}
			res = requests.get("https://blog.nicovideo.jp" + link)
			res.encoding = res.apparent_encoding
			contentSoap = BeautifulSoup(res.text, "html.parser")
			contentAtricles = contentSoap.select("div.article.article-content")

			

			for ca in contentAtricles:
				# 要約したものを掲示する
				contact = ollama.sendOllama("次の内容を1500文字以内で要約してください「" + ca.text + "」")
				rowResult["content"] = ca.text
				rowResult["summary"] = contact

			
			print(rowResult)
			result.append(rowResult)

	return result

		
def GetVOICEROID():
	result = []
	# ニコニコインフォにアクセス
	response = requests.get(VOICEROID_URL)
	response.encoding = response.apparent_encoding
	soup = BeautifulSoup(response.text, "html.parser")
	# 指定の領域の情報を取得
	articles = soup.select("ul#vp_1.l-main.l-main-list2 li.l-main.l-main-list2-item a")

	query = "SELECT link, title FROM niconico_links WHERE delete_flg = 0"
	dbResult = db.select(query)
	for article in articles:
		# タイトルとリンクを取得
		title = article.text.strip()
		link = article['href']
		
		# リンクから過去に取得済みのデータを除外する
		checked = False

		# 公式の誕生祭の場合
		if not(re.match(r"^[0-9]+/[0-9]+.*の誕生日！動画の投稿・視聴・コメントで誕生祭をお祝いしよう【[0-9]+/[0-9]+から】$",title, flags=re.MULTILINE)):
			checked = True

		for rowData in dbResult:

			if rowData[0] == link:
				checked = True

		if checked == False:
			# DBに保存
			query = "INSERT INTO niconico_links( link, title )VALUES( '" + link + "', '" + title + "' )"
			db.insert(query)


			# 該当の記事の内容を取得
			rowResult = {'title' : title, 'content': '', 'summary': '', 'link': "https://blog.nicovideo.jp" + link}
			res = requests.get("https://blog.nicovideo.jp" + link)
			res.encoding = res.apparent_encoding
			contentSoap = BeautifulSoup(res.text, "html.parser")
			contentAtricles = contentSoap.select("div.article.article-content")

			

			for ca in contentAtricles:
				# 要約したものを掲示する
				contact = ollama.sendOllama("次の内容を1500文字以内で要約してください「" + ca.text + "」")
				rowResult["content"] = ca.text
				rowResult["summary"] = contact

			
			print(rowResult)
			result.append(rowResult)

	return result
# def GetUserVideos(userid):

