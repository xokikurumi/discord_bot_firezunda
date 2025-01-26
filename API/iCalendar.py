#pip install ics
from ics import Calendar
from common import http
from common import db

def download():
	content = http.getContent("https://vo.nrsy.jp/event-schedule.ics")
	with open("tmp\\event-schedule.ics", mode='wb') as f:
		f.write(content)


def load():
	with open("tmp\\event-schedule.ics", 'r', encoding='utf-8') as f:
		icsStr = f.read()

	cal = Calendar(icsStr)
	return cal.events

def check(title, date):
	query = "SELECT COUNT(*) FROM auto_send_log WHERE log_key_1='" + title + "' AND log_key_2='" + date + "';"
	queryData = db.select(query)
	return queryData[0][0] == 0

def save(title, date):
	query = "INSERT INTO auto_send_log(log_key_1,log_key_2)VALUES('" + title + "','" + date + "');"
	queryData = db.insert(query)

def sendChannel():
	query = "SELECT server_id,value FROM config WHERE `key` = 'cAaction' AND value != '0';"
	queryData = db.select(query)
	result = []
	for keys in queryData:
		query = "SELECT server_id,value FROM config WHERE server_id= '" + keys[0] + "' AND `key` = 'cAroll' AND value is not null;"
		rollData = db.select(query)
		# print(rollData[0][1])
		resultCal =[
			keys[0],
			keys[1],
			rollData[0][1]
		]
		result.append(resultCal)
		print(result)

	return result

