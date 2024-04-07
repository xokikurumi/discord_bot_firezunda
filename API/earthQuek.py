import json
import re

from common import db
from common import http
from constants import constants


def getChannels(self):
	queryData = db.select("SELECT guild_id,channel_id,mention FROM earth_quake_send;")
#	print(queryData)
	return queryData

def getInfomation(self):
	result = []
	res = http.getJSON("https://api.p2pquake.net/v2/history?codes=551&codes=552&codes=556&limit=10")
	print
	for jd in res:
		query = "SELECT count(*) AS cnt FROM auto_send_log WHERE log_key_1 = '" + jd["id"] + "'"
		queryData = db.select(query)
		
		
		if(queryData[0][0] == 0):
			# IDを登録する
			# 551(地震情報)
			if jd["code"] == '551':
				points = jd["points"]
				if(len(points) > 0):
					query = "INSERT INTO auto_send_log( log_key_1, log_key_2, log_key_3 )VALUES( '" + jd["id"] + "', '" + str(jd["earthquake"]["hypocenter"]["latitude"]) + "', '" + str(jd["earthquake"]["hypocenter"]["longitude"]) + "' )"
					db.insert(query)

					# 過去に投稿されたデータではない場合
					resultData = []
					rowData = '[roll] \n'

					resultData.append([':earth_africa: 【地震速報】 :earth_africa:' ,''])
					#2行目
					resultData.append(['発生時刻' ,jd["issue"]["time"] + ''])
					#3行目
					resultData.append(['震源地' ,jd["earthquake"]["hypocenter"]["name"] + ''])
					resultData.append(['震源の深さ' ,str(jd["earthquake"]["hypocenter"]["depth"]) + 'km' + ''])
					# 4行目
					resultData.append(['マグニチュード' ,str(jd["earthquake"]["hypocenter"]["magnitude"]) + ''])
					resultData.append(['最大震度' ,scale(int(jd["earthquake"]["maxScale"])) + ''])
					# 5行目
					resultData.append(['津波(国内)' ,tsunami(jd["earthquake"]["domesticTsunami"]) + ''])
					resultData.append(['津波(海外)' ,tsunami(jd["earthquake"]["foreignTsunami"]) + ''])
					# 6行目移行

					# 震度情報整理
					scale_10 = []
					scale_20 = []
					scale_30 = []
					scale_40 = []
					scale_45 = []
					scale_50 = []
					scale_55 = []
					scale_60 = []
					scale_70 = []

					image_scale_10 = []
					image_scale_20 = []
					image_scale_30 = []
					image_scale_40 = []
					image_scale_45 = []
					image_scale_50 = []
					image_scale_55 = []
					image_scale_60 = []
					image_scale_70 = []
					
					# 詳細情報の集計
					for point in jd["points"]:

						# 震度1
						if point["scale"] == 10:
							# テキストで送信する場合
							scale_10.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_10.append([point["pref"], point["addr"]])

						# 震度2
						if point["scale"] == 20:
							# テキストで送信する場合
							scale_20.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_20.append([point["pref"], point["addr"]])
						# 震度3
						if point["scale"] == 30:
							# テキストで送信する場合
							scale_30.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_30.append([point["pref"], point["addr"]])

						# 震度4
						if point["scale"] == 40:
							# テキストで送信する場合
							scale_40.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_40.append([point["pref"], point["addr"]])

						# 震度5弱
						if point["scale"] == 45:
							# テキストで送信する場合
							scale_45.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_45.append([point["pref"], point["addr"]])

						# 震度5強
						if point["scale"] == 50:
							# テキストで送信する場合
							scale_50.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_50.append([point["pref"], point["addr"]])

						# 震度6弱
						if point["scale"] == 55:
							# テキストで送信する場合
							scale_55.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_55.append([point["pref"], point["addr"]])

						# 震度6強
						if point["scale"] == 60:
							# テキストで送信する場合
							scale_60.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_60.append([point["pref"], point["addr"]])

						# 震度7
						if point["scale"] == 70:
							# テキストで送信する場合
							scale_70.append([point["pref"], point["addr"]])

							# 画像で送信する用
							image_scale_70.append([point["pref"], point["addr"]])
							
					# 地震情報テキストの生成
					if len(scale_70) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度7】'])
						pref = ''
						for x in scale_70:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])
					
					if len(scale_60) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度6強】'])
						pref = ''
						for x in scale_60:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])

					if len(scale_55) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度6弱】'])
						pref = ''
						for x in scale_55:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])

					if len(scale_50) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度5強】'])
						pref = ''
						for x in scale_50:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])

					if len(scale_45) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度5弱】'])
						pref = ''
						for x in scale_45:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])

					if len(scale_40) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度4】'])
						pref = ''
						for x in scale_40:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])

					if len(scale_30) > 0:
						resultData.append(['', '--------------------------------------------------'])
						resultData.append(['', '【震度3】'])
						pref = ''
						for x in scale_30:
							if(pref == x[0]):
								resultData.append(['', re.sub('.*','　' ,pref) + ' ' + x[1]])
							else:
								pref = x[0]
								resultData.append(['', x[0] + ' ' + x[1]])

					# 速報画像生成
					if (len(scale_70) > 0 or len(scale_60) > 0 or len(scale_55) > 0 or len(scale_50) > 0 or len(scale_45) > 0 or len(scale_40) > 0):
						result.append(resultData)

			# 552(津波予報)
#			if jd["code"] == '552':

			# 556(緊急地震速報（警報）
#			if jd["code"] == '552':
#	print(result)
	return result

def scale(type):
	if type == 10:
		return "震度1"
	if type == 20:
		return "震度2"
	if type == 30:
		return "震度3"
	if type == 40:
		return "震度4"
	if type == 45:
		return "震度5弱"
	if type == 50:
		return "震度5強"
	if type == 55:
		return "震度6弱"
	if type == 60:
		return "震度6強"
	if type == 70:
		return "震度7"
	if type == -1:
		return "震度情報なし"

def tsunami(type):
	if type =="None":
		return "なし"
	if type =="Unknown":
		return "不明"
	if type =="Checking":
		return "調査中"
	if type =="NonEffectiveNearby":
		return "震源の近傍で小さな津波の可能性があるが、被害の心配なし"
	if type =="WarningNearby":
		return "震源の近傍で津波の可能性がある"
	if type =="WarningPacific":
		return "太平洋で津波の可能性がある"
	if type =="WarningPacificWide":
		return "太平洋の広域で津波の可能性がある"
	if type =="WarningIndian":
		return "インド洋で津波の可能性がある"
	if type =="WarningIndianWide":
		return "インド洋の広域で津波の可能性がある"
	if type =="Potential":
		return "一般にこの規模では津波の可能性がある"
	if type =="NonEffective":
		return "若干の海面変動が予想されるが、被害の心配なし"
	if type =="Watch":
		return "津波注意報"
	if type =="Warning":
		return "津波予報(種類不明)"