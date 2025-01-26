from common import db

def msgSplit(msg):
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
	query = "SELECT value FROM config WHERE `key` = '" + key + "' AND server_id = '+ " + str(serverId) + " +';"
	queryResult = db.select(query)
	if value == "@everyone":
		return msg.replace("@roll",value[0])
	else:
		if roll[2] == "none":
			return msg.replace("@roll","")
		else:
			return msg.replace("@roll","<@&"+ value[0] + ">")