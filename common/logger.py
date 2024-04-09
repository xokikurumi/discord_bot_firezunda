import datetime
import os
from common import setting
from common import http

def info(event, msg):
    time = datetime.datetime.now()
    # ログファイル ヘッダー部生成
    logMsg = '[' + time.strftime('%Y/%m/%d %H:%M:%S.%f') + ']'
    if  event.author.bot:
        logMsg += '[BOT name: ' + event.author.name + ']'
    else:
        if event.author.nick == None:
            logMsg += '[name:' + event.author.name+ '/nick: NONE/global: ' + event.author.global_name + ']'
        else:
            logMsg += '[name:' + event.author.name+ '/nick: ' + event.author.nick + '/global: ' + event.author.global_name + ']'
        logMsg += '[' + str(event.id) + ']'
    if (len(event.attachments) > 0):
        logMsg += '[添付ファイルあり]'
        # ダウンロード開始
        for file in event.attachments:
            http.getFileDownload(file,event.guild.name + "\\" + event.channel.name , file.filename)

    else:
        logMsg += '[添付ファイルなし]'

    if (len(event.stickers) > 0):
        logMsg += '[ステッカーあり]'
        for si in event.stickers:
            logMsg += str(si.id) + '@' + si.name
    else:
        logMsg += '[ステッカーなし] '

    # メッセージ本体を生成
    logMsg += '[NEW]' + msg
    if event.author.bot == False:
        print(logMsg)
    # ファイル保存
    filePath = setting.LOG_FILE_PATH + event.guild.name + "\\" + time.strftime('%Y%m%d')
    os.makedirs(filePath, exist_ok=True)

    filePath += '\\' + event.channel.type.name + "_" + str(event.channel.id) + "_" + event.channel.name + ".log"
    file = open(filePath, 'a', encoding='UTF-8')
    file.write(logMsg + "\n")
    file.close()


def info_edit(event, msg):
    time = datetime.datetime.now()
    # ログファイル ヘッダー部生成
    logMsg = '[' + time.strftime('%Y/%m/%d %H:%M:%S.%f') + ']'
    if  event.author.bot:
        logMsg += '[BOT]'
    else:
        if event.author.nick == None:
            logMsg += '[NAME:' + event.author.name+ '/NICK: NONE/GLOBAL: ' + event.author.global_name + ']'
        else:
            logMsg += '[NAME:' + event.author.name+ '/NICK: ' + event.author.nick + '/GLOBAL: ' + event.author.global_name + ']'
        logMsg += '[' + str(event.id) + ']'
    if (len(event.attachments) > 0):
        logMsg += '[添付ファイルあり]'
    else:
        logMsg += '[添付ファイルなし]'

    if (len(event.stickers) > 0):
        logMsg += '[ステッカーあり]'
        for si in event.stickers:
            logMsg += str(si.id) + '@' + si.name
    else:
        logMsg += '[ステッカーなし] '

    # メッセージ本体を生成
    logMsg += '[EDIT]' + msg
    if event.author.bot == False:
        print(logMsg)
    # ファイル保存
    filePath = setting.LOG_FILE_PATH + event.guild.name + "\\" + time.strftime('%Y%m%d')
    os.makedirs(filePath, exist_ok=True)

    filePath += '\\' + event.channel.type.name + "_" + str(event.channel.id) + "_" + event.channel.name + ".log"
    file = open(filePath, 'a', encoding='UTF-8')
    file.write(logMsg + "\n")
    file.close()

def info_delete(event, msg):
    time = datetime.datetime.now()
    # ログファイル ヘッダー部生成
    logMsg = '[' + time.strftime('%Y/%m/%d %H:%M:%S.%f') + ']'
    if  event.author.bot:
        logMsg += '[BOT]'
    else:
        if event.author.nick == None:
            logMsg += '[NAME:' + event.author.name+ '/NICK: NONE/GLOBAL: ' + event.author.global_name + ']'
        else:
            logMsg += '[NAME:' + event.author.name+ '/NICK: ' + event.author.nick + '/GLOBAL: ' + event.author.global_name + ']'
        logMsg += '[' + str(event.id) + ']'
    if (len(event.attachments) > 0):
        logMsg += '[添付ファイルあり]'
    else:
        logMsg += '[添付ファイルなし]'

    if (len(event.stickers) > 0):
        logMsg += '[ステッカーあり]'
        for si in event.stickers:
            logMsg += str(si.id) + '@' + si.name
    else:
        logMsg += '[ステッカーなし] '

    # メッセージ本体を生成
    logMsg += '[EDIT]' + msg
    if event.author.bot == False:
        print(logMsg)
    # ファイル保存
    filePath = setting.LOG_FILE_PATH + event.guild.name + "\\" + time.strftime('%Y%m%d')
    os.makedirs(filePath, exist_ok=True)

    filePath += '\\' + event.channel.type.name + "_" + str(event.channel.id) + "_" + event.channel.name + ".log"
    file = open(filePath, 'a', encoding='UTF-8')
    file.write(logMsg + "\n")
    file.close()


def info_voiceStatus(event, msg):
    time = datetime.datetime.now()
    # ログファイル ヘッダー部生成
    logMsg = '[' + time.strftime('%Y/%m/%d %H:%M:%S.%f') + ']'
    logMsg += '[VOICE_STATUS]'
    logMsg += '[NONE]'
    logMsg += '[NONE]'
    logMsg += '[NONE]'
    # メッセージ本体を生成
    logMsg += '[NEW]' + msg
    
    print(logMsg)
    # ファイル保存
    filePath = setting.LOG_FILE_PATH + 'VoiceChannel' + "\\" + time.strftime('%Y%m%d')
    os.makedirs(filePath, exist_ok=True)

    filePath += '\\' + str(event.channel.id) + "_" + event.channel.name + ".log"
    file = open(filePath, 'a', encoding='UTF-8')
    file.write(logMsg + "\n")
    file.close()


def info_reaction(reaction, user, msg):
    time = datetime.datetime.now()
    # ログファイル ヘッダー部生成
    logMsg = '[' + time.strftime('%Y/%m/%d %H:%M:%S.%f') + ']'
    if user.nick == None:
        logMsg += '[name:' + user.name+ '/nick: NONE/global: ' + user.global_name + ']'
    else:
        logMsg += '[name:' + user.name+ '/nick: ' + user.nick + '/global: ' + user.global_name + ']'

    logMsg += '[' + str(reaction.message.id) + ']'

    # 添付ファイルなし
    logMsg += '[NONE]'

    logMsg += '[NONE] '

    # メッセージ本体を生成
    print(type(reaction.emoji))
    if type(reaction.emoji) is str:
        logMsg += '[REACTION]' + reaction.emoji + ' count: ' + str(reaction.count) + ' Message: ' + msg
    else:
        logMsg += '[REACTION]<' + reaction.emoji.name + ':' + str(reaction.emoji.id) + '> count: ' + str(reaction.count) + ' Message: ' + msg
    print(logMsg)
    
    # ファイル保存
    filePath = setting.LOG_FILE_PATH + reaction.message.guild.name + "\\" + time.strftime('%Y%m%d')
    os.makedirs(filePath, exist_ok=True)

    filePath += '\\' + reaction.message.channel.type.name + "_" + str(reaction.message.channel.id) + "_" + reaction.message.channel.name + ".log"
    file = open(filePath, 'a', encoding='UTF-8')
    file.write(logMsg + "\n")
    file.close()