import websocket
import json
import re
import time
try:
    import thread
except ImportError:
    import _thread as thread

from common import db
from common import http
from constants import constants
from service import createMapImages

def getInfomation(self):

	result = []
	# 本番用
	res = http.getJSON("https://api.p2pquake.net/v2/history?codes=551&codes=552&codes=556&limit=10")
	print
	for jd in res:
		query = "SELECT count(*) AS cnt FROM auto_send_log WHERE log_key_1 = '" + jd["id"] + "'"
		queryData = db.select(query)

		imageLocations 		= []
		imageLatitudes 		= []
		imageLongitudes 	= []
		imageIntensities 	= []
		epicenter           = {
			'場所' : jd["earthquake"]["hypocenter"]["name"],
			'緯度' : str(round(jd["earthquake"]["hypocenter"]["latitude"],1)),
			'経度' : str(round(jd["earthquake"]["hypocenter"]["longitude"],1)),
			'震度' : jd["earthquake"]["maxScale"],
			'時刻' : jd["issue"]["time"]
		}
		imageArea = {
			'lon_min': 30000.0,
			'lat_min': 30000.0,
			'lon_max': 0.0,
			'lat_max': 0.0
			}

			
		if(queryData[0][0] == 0):
			# 地震速報
			# IDを登録する
			if (jd["code"] == 551):
				points = jd["points"]
				if(len(points) > 0):
					if int(jd["earthquake"]["maxScale"]) <= 30:
						continue

					query = "INSERT INTO auto_send_log( log_key_1, log_key_2, log_key_3 )VALUES( '" + jd["id"] + "', '" + str(jd["earthquake"]["hypocenter"]["latitude"]) + "', '" + str(jd["earthquake"]["hypocenter"]["longitude"]) + "' )"
					db.insert(query)

					# 最大深度が3以下の場合はスキップ

					# 過去に投稿されたデータではない場合
					resultData = []
					rowData = "[roll] \n"
					rowDataBody = ""

					rowData += "# :earth_africa: 【地震速報】 :earth_africa:\n"
					rowData += "===========================================\n"
					rowData += "発生時刻: " + jd["issue"]["time"] + "\n"
					rowData += "震源地: " + jd["earthquake"]["hypocenter"]["name"] + "\n"
					rowData += "震源の深さ: " + str(jd["earthquake"]["hypocenter"]["depth"]) + "km" + "\n"
					rowData += "マグニチュード: " + str(jd["earthquake"]["hypocenter"]["magnitude"]) + "\n"
					rowData += "最大震度: " + scale(int(jd["earthquake"]["maxScale"])) + "\n"
					rowData += "津波(国内): " + tsunami(jd["earthquake"]["domesticTsunami"]) + "\n"
					rowData += "津波(海外): " + tsunami(jd["earthquake"]["foreignTsunami"]) + "\n"
					rowData += "===========================================\n"

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
					
					for point in jd["points"]:

						# 緯度経度を検索
						
						query = "SELECT count(*) AS cnt FROM locations WHERE pref = '" + point["pref"] + "' AND addr = '" + point["addr"] + "'"
						queryData = db.select(query)
						if(queryData[0][0] != 0):
							query = "SELECT longitude, latitude FROM locations WHERE pref = '" + point["pref"] + "' AND addr = '" + point["addr"] + "'"
							queryData = db.select(query)


							if point["scale"] >= 30:
								imageLongitudes.append(queryData[0][0])
								imageLatitudes.append(queryData[0][1])

								# 緯度経度の最大と最小値を算出
								imageArea["lon_min"] = min(float(imageArea["lon_min"]), round(float(queryData[0][0]),1))
								imageArea["lon_max"] = max(float(imageArea["lon_max"]), round(float(queryData[0][0]),1))
								imageArea["lat_min"] = min(float(imageArea["lat_min"]), round(float(queryData[0][1]),1))
								imageArea["lat_max"] = max(float(imageArea["lat_max"]), round(float(queryData[0][1]),1))

								imageLocations.append(point["addr"])
								imageIntensities.append(scale(int(point["scale"])))

						else:
							# DBにない場合は国土地理院から引用
							geoRes = http.getJSON("https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + point["pref"] + point["addr"])

							if (len(geoRes) > 0):
								query = "INSERT INTO locations( pref, addr, longitude, latitude )VALUES( '" + point["pref"] + "', '" + point["addr"] + "', '" + str(round(geoRes[0]["geometry"]["coordinates"][0],1)) + "', '" + str(round(geoRes[0]["geometry"]["coordinates"][1],1)) + "' )"
								db.insert(query)

								if point["scale"] >= 30:
									imageLongitudes.append(round(geoRes[0]["geometry"]["coordinates"][0],1))
									imageLatitudes.append(round(geoRes[0]["geometry"]["coordinates"][1],1))

									# 緯度経度の最大と最小値を算出
									imageArea["lon_min"] = min(imageArea["lon_min"], round(geoRes[0]["geometry"]["coordinates"][0],1))
									imageArea["lon_max"] = max(imageArea["lon_max"], round(geoRes[0]["geometry"]["coordinates"][0],1))
									imageArea["lat_min"] = min(imageArea["lat_min"], round(geoRes[0]["geometry"]["coordinates"][1],1))
									imageArea["lat_max"] = max(imageArea["lat_max"], round(geoRes[0]["geometry"]["coordinates"][1],1))

									imageLocations.append(point["addr"])
									imageIntensities.append(scale(int(point["scale"])))
							
							

						if point["scale"] == 10:
							# テキストで送信する場合
							scale_10.append([point["pref"], point["addr"]])

						if point["scale"] == 20:
							# テキストで送信する場合
							scale_20.append([point["pref"], point["addr"]])

						if point["scale"] == 30:
							# テキストで送信する場合
							scale_30.append([point["pref"], point["addr"]])

						if point["scale"] == 40:
							# テキストで送信する場合
							scale_40.append([point["pref"], point["addr"]])

						if point["scale"] == 45:
							# テキストで送信する場合
							scale_45.append([point["pref"], point["addr"]])

						if point["scale"] == 50:
							# テキストで送信する場合
							scale_50.append([point["pref"], point["addr"]])

						if point["scale"] == 55:
							# テキストで送信する場合
							scale_55.append([point["pref"], point["addr"]])

						if point["scale"] == 60:
							# テキストで送信する場合
							scale_60.append([point["pref"], point["addr"]])

						if point["scale"] == 70:
							# テキストで送信する場合
							scale_70.append([point["pref"], point["addr"]])

						if point["scale"] == -1:
							print("Non Scale")


					# 地震情報テキストの生成
					if len(scale_70) > 0:
						
						rowDataBody += "## 【震度7】\n"
						pref = ""
						for x in scale_70:
							if (pref == x[0]):
								rowDataBody = rowDataBody + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowDataBody = rowDataBody + x[0] + " " + x[1] + "\n"
					
					if (len(scale_60) > 0):
						rowDataBody += "## 【震度6強】\n"
						pref = ""
						for x in scale_60:
							if(pref == x[0]):
								rowDataBody = rowDataBody + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowDataBody = rowDataBody + x[0] + " " + x[1] + "\n"

					if (len(scale_55) > 0):
						rowDataBody += "## 【震度6弱】\n"
						pref = ""
						for x in scale_55:
							if(pref == x[0]):
								rowData = rowData + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowData = rowData + x[0] + " " + x[1] + "\n"
								

					if (len(scale_50) > 0):
						rowDataBody += "## 【震度5強】\n"
						pref = ""
						for x in scale_50:
							if(pref == x[0]):
								rowDataBody = rowDataBody + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowDataBody = rowDataBody + x[0] + " " + x[1] + "\n"
								

					if (len(scale_45) > 0):
						rowDataBody += "### 【震度5弱】\n"
						pref = ""
						for x in scale_45:
							if(pref == x[0]):
								rowDataBody = rowDataBody + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowDataBody = rowDataBody + x[0] + " " + x[1] + "\n"
								

					if (len(scale_40) > 0):
						rowDataBody += "### 【震度4】\n"
						pref = ""
						for x in scale_40:
							if(pref == x[0]):
								rowDataBody = rowDataBody + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowDataBody = rowDataBody + x[0] + " " + x[1] + "\n"
								

					if (len(scale_30) > 0):
						rowDataBody += "### 【震度3】\n"
						pref = ""
						for x in scale_30:
							if(pref == x[0]):
								rowDataBody = rowDataBody + re.sub(".*","　" ,pref) + " " + x[1] + "\n"
							else:
								pref = x[0]
								rowDataBody = rowDataBody + x[0] + " " + x[1] + "\n"

					# 表示エリア拡大
					imageArea["lon_min"] = float(imageArea["lon_min"]) - 1.0
					imageArea["lon_max"] = float(imageArea["lon_max"]) + 1.0
					imageArea["lat_min"] = float(imageArea["lat_min"]) - 1.0
					imageArea["lat_max"] = float(imageArea["lat_max"]) + 1.0

					resultData.append(rowData)
					resultData.append(rowDataBody)
					result.append(resultData);
			# END IF

			if (jd["code"] == 552):
				# 津波情報
				rowResult = ""

				# IDと時間 登録
				query = "INSERT INTO auto_send_log( log_key_1, log_key_2, log_key_3 )VALUES( '" + jd["id"] + "', '" + str(jd["time"]) + "', '' )"
				db.insert(query)

				# キャンセルフラグチェック
				if (bool(jd["cancelled"])):
					rowResult = "各津波予報が解除されました。"
				else:
					areas = jd["areas"]
					if(len(areas) > 0):
						# 発令された場所がある場合
						for area in areas:
							rowResult = rowResult + area["name"] + " -> " + area["firstHeight"]["condition"]
							rowResult = rowResult  + " -> 最大: " + area["maxHeight"]["description"] + "\n"
						# END FOR
					# END IF
				# END IF
				result.append(rowResult)
			# END IF

			# 地震情報設定
			earthQuake = [
				imageArea
				, epicenter
				, imageLocations
				, imageLatitudes
				, imageLongitudes
				, imageIntensities
			]

			# 津波情報設定
			tsunami = [
				# 北海道


				# 青森県


				# 岩手県


				# 宮城県


				# 秋田県


				# 山形県


				# 福島県


				# 茨城県


				# 栃木県


				# 群馬県


				# 埼玉県


				# 千葉県


				# 東京都


				# 神奈川県


				# 新潟県


				# 富山県


				# 石川県


				# 福井県


				# 山梨県


				# 長野県


				# 岐阜県


				# 静岡県


				# 愛知県


				# 三重県


				# 滋賀県


				# 京都府


				# 大阪府


				# 兵庫県


				# 奈良県


				# 和歌山県


				# 鳥取県


				# 島根県


				# 岡山県


				# 広島県


				# 山口県


				# 徳島県


				# 香川県


				# 愛媛県


				# 高知県


				# 福岡県


				# 佐賀県


				# 長崎県


				# 熊本県


				# 大分県


				# 宮崎県


				# 鹿児島県


				# 沖縄県


			]

			# 画像生成処理
			if not((imageArea["lon_min"] == 30000.0 and imageArea["lat_min"] == 30000.0 and imageArea["lon_max"] == 0.0 and imageArea["lat_max"] == 0.0) and len(tsunami) == 0):
				createMapImages.createImages(earthQuake, tsunami, "nowQuakeImages")



	#print(result)
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