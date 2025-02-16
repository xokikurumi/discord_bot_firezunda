import re
import json
import random
from common import http

def getResultDice(msg):
    # httpLog = http.getJSON("https://bcdice.onlinesession.app/v2/game_system/DiceBot/roll?command=" + str)
    

    
    total = 0
    result = "("+ msg + ") "
    resultStr = ''
    msg = msg.replace(" ", "")
    if re.findall('[+\\-\\*/%\\^]',msg):
        dices = re.split('[+\\-\\*/%\\^]',msg)
        diceResult = []
        mathRegular = msg
        
        # 計算事前処理を行う
        for i in range(1, len(dices) + 1):

            mathRegular = mathRegular.replace(dices[(i - 1)],"${" + str(i) + "}", 1)
        
        # 乱数からダイスを投げる
        for dice in dices:
            if re.findall('[dD]', dice):
                diceRow = re.split(r'[dD]', dice)
                if int(dice[0]) == 1:
                    diceResult.append(random.randint(1, int(diceRow[1])))
                else:
                    diceTotal = 0
                    for r in range(0, int(diceRow[0])):
                        diceTotal = diceTotal + random.randint(1, int(diceRow[1]))
                    
                    diceResult.append(diceTotal)
            else:
                diceResult.append(int(dice))

        # 事前処理を行った後計算用に置き換える
        for i in range(1, len(dices) + 1):
            mathRegular = mathRegular.replace("${" + str(i) + "}", str(diceResult[(i - 1)]), 1)

        # 計算処理を行う
        total = eval(mathRegular)

        result = result + "> (" + mathRegular + ") > " + str(total)

        # 以下は判定の結果を反映

    elif re.findall('[dD]', msg) :

        dice = re.split('[dD]', msg)
        diceResult = dice(msg)
        if int(dice[0]) != 1:
            resultStr = " > " + str(diceResult.total) + "[" + diceResult.resultStr[:-2] + "]"

        result = result + resultStr + " > " + str(diceResult.total)

        # 以下は判定の結果を反映

    elif re.findall('[bB]', msg):
        dice = dice(msg)

        if int(dice[0]) != 1:
            resultStr = " > " + dice.resultStr[:-2]

        result = result + resultStr


    return result


def isDice(str):

    result = False
    # 文字を小文字に変換
    str = str.lower()
    # 世紀表現によるダイスロール判定
    if(re.findall('^S?([+\\-(]*(\\d+|D\\d+)|\\d+B\\d+|\\d+T[YZ]\\d+|C[+\\-(]*\\d+|choice|D66|(repeat|rep|x)\\d+|\\d+R\\d+|\\d+U\\d+|BCDiceVersion)',str)):
        
        result = True
    # end if

    return  result

def dice(str):
    result = {
        # 合計値
        "total" : 0,

        # ダイスのログ(10, 5......)
        "diceResult" : "",
    }
    total = 0
    resultStr = ""
    dice = re.split("[bdBD]",str)
    if int(dice[0]) == 1:
        resultStr = random.randint(1, int(dice[1]))
    else:
        for r in range(0, int(dice[0])):
            row = random.randint(1, int(dice[1]))
            print(str(row))
            total = total + row
            resultStr = resultStr + str(row) + ", "
    
    # 結果を反映
    result["total"] = total
    result["diceResult"] = resultStr
    return result


def judgment (msg, total):
    # 判定処理
    result = ""
    if re.findall('[<>=!]=*'):
        # 判定結果反映あり
        
        judg = 0
        for dice in re.split('[+\\-\\*/%\\^]',msg):
            if not re.findall("[dD]", dice):
                # 数字のみ
                judg = int(dice)

        # if judg > 0:
        #     # 判定するのが一方が固定値の場合




        
    return result
