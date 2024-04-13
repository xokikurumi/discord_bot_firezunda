import geopandas as gpd
import matplotlib.pyplot as plt
import datetime
from geopy.geocoders import Nominatim

def createEarthQuakeMap(data, point_occurrence):
	# 画像を生成する
	map = Basemap(llcrnrlon = 122, llcrnrlat=20,urcrnrlon=155,urcrnrlat=47)
	lonMax = point_occurrence[0]
	lonMin = 0.0
	latMax = point_occurrence[1]
	latMin = 0.0
	# 震源地はXで表示する
	plt.plot(point_occurrence[0], point_occurrence[1],marker='xD', color='#FF0000')

	geolocator = Nominatim(user_agent='geoapiExercises')
	for d in data:
		# 位置情報を取得
		location = geolocator.geocode(data[0] + ' ' + data[1])
		map(location.longitude,location.latitude)
		# 各地域ごとの震度は気象庁で定義されている「カラースキーム(第二版)」と同じ色を使用する
		plt.plot(location, location[1],marker=getMarker(location[2]), color=getColor(location[2]))

def  getColor(scale):
	scaleMap = {
		# 震度1
		"1": "#3C5A82"
		# 震度2
		"2": "#1E82E6"
		# 震度3
		"3": "#78E6DC"
		# 震度4
		"4": "#FFFF96"
		# 震度5弱
		"5m": "#FFD200"
		# 震度5強
		"5": "#FF9600"
		# 震度6弱
		"6m": "#F03200"
		# 震度6強
		"6": "#BE0000"
		# 震度7
		"7": "#8C0028"
	}
	return scaleMap[scale]

def  getMarker(scale):
	scaleMap = {
		# 震度1
		"1": '$❶$'
		# 震度2
		"2": '$❷$'
		# 震度3
		"3": '$❸$'
		# 震度4
		"4": '$❹$'
		# 震度5弱
		"5m": '$❺$'
		# 震度5強
		"5": '$❺$'
		# 震度6弱
		"6m": '$❻$'
		# 震度6強
		"6": '$❻$'
		# 震度7
		"7": '$❼$'
	}
	return scaleMap[scale]
