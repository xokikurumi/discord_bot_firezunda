import os
import requests
import re
import datetime
from common import setting
from constants import constants




def getFileDownload(url,channelName, filename):
    time = datetime.datetime.now()

    urlData = requests.get(url).content
    filePath = setting.LOG_FILE_PATH + 'upload\\' + time.strftime('%Y%m%d') + '\\' + channelName
    os.makedirs(filePath, exist_ok=True)

    with open(filePath + '\\' + filename ,mode='wb') as f:
      f.write(urlData)


def getText(url):
    time = datetime.datetime.now()

    urlData = requests.get(url)
    return urlData.text

def getJSON(url):
    time = datetime.datetime.now()

    urlData = requests.get(url)
    return urlData.json()

def getContent(url):
    time = datetime.datetime.now()

    urlData = requests.get(url)
    return urlData.content

def format(html):
    html = re.sub("<(br|BR)>","\n", html)
    html = re.sub("<(P|p)>","", html)
    html = re.sub("</(P|p)>","\n", html)
    html = re.sub("<(div|DIV) .+?>","", html)
    html = re.sub("</(div|DIV)>","\n", html)
    html = re.sub("<.+?>", "", html)
    html = re.sub("■", "## ■", html)
    for num in range(len(constants.replaceFrom)):
        html = replace(constants.replaceFrom[num], constants.replaceTo[num])
    return html    
