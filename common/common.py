
def msgSplit(msg):
	msgs = msg.split()
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