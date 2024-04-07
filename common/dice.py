import re
import json
from common import http

def getResultDice(str):
    httpLog = http.getJSON("https://bcdice.onlinesession.app/v2/game_system/DiceBot/roll?command=" + str)

    return httpLog


def isDice(str):

    result = False
    # 文字を小文字に変換
    str = str.lower()
    # 世紀表現によるダイスロール判定
    if(re.findall('^S?([+\\-(]*(\\d+|D\\d+)|\\d+B\\d+|\\d+T[YZ]\\d+|C[+\\-(]*\\d+|choice|D66|(repeat|rep|x)\\d+|\\d+R\\d+|\\d+U\\d+|BCDiceVersion)',str)):
        
        result = True
    # end if

    return  result