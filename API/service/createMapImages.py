import geopandas as gpd
import matplotlib.pyplot as plt
import datetime

def createEarthQuakeMap(pref, value):
	# 速報時刻設定
	time = datetime.datetime.now()

	plt.title('地震速報 (' + time.strftime('%Y/%m/%d %H:%M:%S') + '時点)')
	plt.axis('off')

	# Shapefileを読み込む
	fp = "N03-20210101_GML/N03-21_210101.shp"
	japan = gpd.read_file(fp, encoding="cp932")

	df = japan[japan['N03_001'].isin(pref)]

	fig, ax = plt.subplots(figsize=(10, 6))
	
	# 軸を非表示にする
	ax.axis('off')

	# アスペクト比を 1 にする
	ax.set_aspect('equal', 'datalim')

	df.plot(ax=ax, edgecolor='black', facecolor='aliceblue', linewidth=0.5)

	# 図面を表示する
	plt.show()