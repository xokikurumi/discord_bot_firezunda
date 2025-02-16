from common import db

def msgSplit(msg):
	msg = msg.replace("\r","\n")
	msgs = msg.split("\n")
	result = []
	resultData = ""
	for x in msgs:
		if len(resultData + x) < 2000:
			resultData = resultData + x + '\n'
		else:
			result.append(resultData)
			resultData = x

	result.append(resultData)
	return result

def msgRoll(msg,key, serverId):
	query = "SELECT value FROM config WHERE `key` = '" + key + "' AND server_id = '" + str(serverId) + "';"
	print(query)
	queryResult = db.select(query)
	print(queryResult)
	if str(queryResult[0][0]) == "@everyone":
		return msg.replace("@roll","@everyone")
	else:
		if queryResult[0][0] == "none":
			return msg.replace("@roll","")
		else:
			return msg.replace("@roll","<@&"+ queryResult[0][0] + ">")