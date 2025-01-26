import discord
import re
import emoji
# pip install emoji
import datetime
from datetime import timedelta


#pip install ics
from ics import Calendar

from discord import Intents, Client, Interaction, EntityType, PrivacyLevel
from common import logger
from common import dice
from common import common
# from API import earthQuek
from discord.ext import commands
from discord.ext import tasks
from constants import token

from API import niconico
from API import earthQuek
from API import iCalendar
# from googletrans import Translator
# pip install googletrans==4.0.0rc1

# 英語のみ反応させる
# 他の言語は気が向いたら
def isLang(msg):
    # 前提処理
    # 絵文字削除
    msg = emoji.replace_emoji(msg)
    msg = re.sub('^https?://[\\w/:%#\\$&\\?\\(\\)~\\.=\\+\\-]+$', '', msg)

    #判定処理
    result = False
    checkList = [
        '^https?://[\\w/:%#\\$&\\?\\(\\)~\\.=\\+\\-]+$',
        '[ぁ-んーァ-ヶｱ-ﾝﾞﾟ一-龠]+',
        '^((<:[a-zA-Z0-9]+:[0-9]+>)|(:.+:))+$',
        '^[0-9]+.*',
        '^!',
        '^<@&[0-9]+>',
        '^[0-9]+',
        '^[wW]+',
        '\\[.*\\]\\(https?://[\\w/:%#\\$&\\?\\(\\)~\\.=\\+\\-]+\\)'
    ]

    # 英語のみに設定
    if(re.findall('([ -~\\n]+)',msg)):
        # あ
        for x in checkList:
            if not(re.findall(x,msg)):
                result = True
            else:
                result = False
                break

    # 英文かどうかをチェック
    if result:
        if(not(re.match(r"^([A-Z@\*#\s][A-Za-z0-9\*_#]*)([A-Za-z0-9:<>\n\s/\.,'-?!\*_]+)([\s.\?\!:\n_])+$",msg, flags=re.MULTILINE))):
            result = False

    return result

class MyClient(discord.Client):



    async def on_ready(self):
        client.earthQuek.start()

        print('Logged on as', self.user)
        # self.earthQuek.start()

    # 通常のメッセージが送信された場合
    async def on_message(self, message):
        # don't respond to ourselves
        logger.info(message, message.content)
        if message.author == self.user:
            return

        # ダイスチェック
        if dice.isDice(message.content):
            diceLog = dice.getResultDice(message.content)

            if(diceLog["ok"]):
                await message.channel.send(diceLog["text"])
                return

        if(isLang(re.sub(r'[<@]+[:A-Za-z0-9]+[>]',"",message.content))):
            if message.author.bot:
                # マイクラbot,v1除外
                if not(message.author.id == 1066346686127026236 or message.author.id == 986560084891041892):
                    tr = Translator()
                    result = tr.translate(re.sub(r'[<@]+[:A-Za-z0-9]+[>]',"",message.content),src='en',dest='ja').text
                    result = re.sub('[<＜][0-9a-zA-Z]+[:：][0-9a-zA-Z]*[>＞]', '', result)
                    result = re.sub('[:：][0-9][:：]', '', result)
                    # 正規表現を使用し、絵文字を削除する
                    msgs = common.msgSplit(result)
                    
                    for msg in msgs:
                        await message.channel.send(msg)
                    
                    return

#         if message.content.startswith("入るぞ、ポプ子。大丈夫だ、私一人だ。武器も持っていない。ポプ子、終わりだ。もう逃げることはできない、狙撃手が狙っている。見ろ、この騒動を。ここはベトナムじゃない、アメリカだ。戦争は終わったんだ！"):
#             await message.channel.send('''なにも終わっちゃいない！なにも終わっちゃいないんだ！！
# アタイにとって戦争は続いたままなんだ！
# 自分の金で買った好きな洋服をdisられている！
# SNS上ではクソダサいだのみんな好き放題に言いやがる！
# あいつら、なんなんだ！！何も知らないくせに！！！''')
#         if message.content.startswith("<@1208286469953953833>"):
#             await message.channel.send('''なにも終わっちゃいない！なにも終わっちゃいないんだ！！
# アタイにとって戦争は続いたままなんだ！
# 自分の金で買った好きな洋服をdisられている！
# SNS上ではクソダサいだのみんな好き放題に言いやがる！
# あいつら、なんなんだ！！何も知らないくせに！！！''')

#         if message.content.startswith("服のセンスが悪かったんだ"):
#             await message.channel.send('''悪かった！？私の時代はいつ来るんだ！！
# 少なくともファッション誌には載っていた服だぞ！？''')

#         if message.content.startswith("自称ファッションリーダーがこんなところで死ぬのか？"):
#             await message.channel.send('''アタイ・・・、アニメであらゆるかわいいキャラをやらせてもらった。
# だが、イベントに出ると大喜利ばっかりやらされる！
# 帰ってくるんじゃなかったぁ・・・！！
# ちやほやされたかった、みんなみたいに・・・。
# だけど、もう引き返せないとこまで来ちまったんだ！！
# あたしゃバラエティ声優だよぉ・・・！！！
# 毎日夢を見るんだ・・・。
# 川柳大喜利がすべった時の夢を・・・。''')

        # if message.content == 'ping':
        #     await message.channel.send('pong')
        # 管理者権限系コマンド
        # bot以外
        if message.author.bot:
            return
        if message.author.guild_permissions.administrator:
            if message.content == "?fireConfig help":
                await message.channel.send('''
## 管理者専用コマンド一覧

                ''')

            # if message.content.startswith("?fireConfig"):
            #     result = commands.configCmd(message, message.content)
            #     print(result)
            #     for msg in result:
            #         await message.channel.send(msg)

        # その他ユーザ向けコマンド

    ## 以下は全てログ取得系のイベント
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            logger.info_edit(before, "before: " + before.content + ' -> after:' + after.content)

    async def on_message_delete(self, message):
        logger.info(message, "Message delete from: " + message.content)

    async def on_voice_state_update(self, member, before, after):
        if before.channel == None:

            logger.info_voiceStatus(after, member.name + ' がボイスチャンネルに参加')
        elif after.channel == None:

            logger.info_voiceStatus(before, member.name + ' がボイスチャンネルを退出')


    @tasks.loop(seconds=1)
    async def earthQuek(self):
        dt_now = datetime.datetime.now().strftime("%M%S")
        dt_now_m = datetime.datetime.now().strftime("%m")
        dt_now_d = datetime.datetime.now().strftime("%d")
        # print(dt_now)
        # Monthly
        if int(dt_now_d) == 1:
            # 二か月に一度実行
            if (int(dt_now_m) %2) == 0:
                # 同人即売会登録
                iCalendar.download()
                evntCal = Calendar()
                for event in iCalendar.load():
                    if int(datetime.datetime.now().strftime("%Y%m%d")) < int(event.begin.datetime.strftime("%Y%m%d")):
                        if iCalendar.check(event.name,event.begin.datetime.strftime("%Y/%m/%d")):
                            # print(event.name)
                            # print(event.begin.datetime.strftime("%Y/%m/%d"))
                            iCalendar.save(event.name,event.begin.datetime.strftime("%Y/%m/%d"))
                            # 登録済みかどうかのチェック
                            startdt = event.begin.datetime
                            startdt = startdt + timedelta(hours=-9)
                            enddt = event.end.datetime
                            enddt = enddt + timedelta(hours=15)
                            for roll in iCalendar.sendChannel():
                                # 登録処理
                                print(roll)
                                await self.get_guild(int(roll[0])).create_scheduled_event(
                                    name=event.name,
                                    description=event.description,
                                    start_time=startdt,
                                    end_time=enddt,
                                    location=event.location,
                                    entity_type=EntityType.external,
                                    privacy_level=PrivacyLevel.guild_only)
                                # 登録後の通知処理
                                self.get_guild(int(roll[0])).get_channel(int(roll[1])).send(common.msgRoll("@roll\n" + event.name + "(" + event.begin.datetime.strftime("%Y/%m/%d") + " 開催) を登録しました。"
                                    , roll[2], int(roll[0])))


            # # 半年に一度実行
            # if int(dt_now_m) %6 == 0:
            #     await self.get_guild(934440828041035796).send("")
            # END IF
        # END IF
        # Daily
        if dt_now == "0000":
            # メンテナンス情報
            result = niconico.GetMaintenance()
            query = "SELECT server_id, value FROM config WHERE `key` = 'nicoInfo';"
            queryResult = db.select(query)
            for row in result:
                # print(row)
                for key in row.keys():
                    msg = "@roll\n"
                    msg = msg +"# " + row["title"] + "\n"
                    msg = msg + row["summary"] + "\n"
                    msg = msg + "\n\n※Ollama(AI) によって内容を要約しています。"
                    msg = msg + "\n元の記事は[こちら]("+ row["link"] +")"
                    msgs = common.msgSplit(msg)

                # 文字数制限に気を付けつつ送信
                for m in msgs:
                    # await message.channel.send(m)
                    for val in queryResult:
                        query = "SELECT server_id, value FROM config WHERE `key` = 'nicoCH';"
                        channelResult = db.select(query)
                        await self.get_guild(queryResult[0][0]).get_channel(channelResult[0][1]).send(common.msgRoll(m, 'nicoInfo', queryResult[0][0]))
            # 誕生祭情報
            result = niconico.GetVOICEROID()
            query = "SELECT server_id, value FROM config WHERE `key` = 'vocaloid';"
            queryResult = db.select(query)
            for row in result:
                # print(row)
                for key in row.keys():
                    msg = "@roll\n"
                    msg = msg +"# " + row["title"] + "\n"
                    msg = msg + row["summary"] + "\n"
                    msg = msg + "\n\n※Ollama(AI) によって内容を要約しています。"
                    msg = msg + "\n元の記事は[こちら]("+ row["link"] +")"

                    msgs = common.msgSplit(msg)

                # 文字数制限に気を付けつつ送信
                for m in msgs:
                    # await message.channel.send(m)
                    for val in queryResult:
                        query = "SELECT server_id, value FROM config WHERE `key` = 'vocaCH';"
                        channelResult = db.select(query)
                        await self.get_guild(queryResult[0][0]).get_channel(channelResult[0][1]).send(common.msgRoll(m, 'vocaloid', queryResult[0][0]))

        # 地震/津波速報
        # 毎秒
        result = earthQuek.getInfomation(self)
        query = "SELECT server_id, value FROM config WHERE `key` = 'quake';"
        queryResult = db.select(query)

        for txt in result:
            # 文字列を2000文字前後(改行コード毎計算)毎にデータを成形
            if len(result) == 1:
                msgs = common.msgSplit(txt)
                index = 0
                for m in msgs:
                    for val in queryResult:
                        query = "SELECT server_id, value FROM config WHERE `key` = 'quakeCH';"
                        channelResult = db.select(query)
                        if index == 0:
                            await self.get_guild(int(queryResult[0][0])).get_channel(int(channelResult[0][1])).send(common.msgRoll(m, 'quake', queryResult[0][0]), file=discord.File("nowQuakeImages.png"))
                        else:
                            await self.get_guild(int(queryResult[0][0])).get_channel(int(channelResult[0][1])).send(common.msgRoll(m, 'quake', queryResult[0][0]))
                    index += 1
            else:
                for msg in txt:
                    #print(msg)
                    msgs = common.msgSplit(msg)
                    index = 0
                    for m in msgs:
                        for val in queryResult:
                            query = "SELECT server_id, value FROM config WHERE `key` = 'quakeCH';"
                            channelResult = db.select(query)
                            if index == 0:
                                await self.get_guild(int(queryResult[0][0])).get_channel(int(channelResult[0][1])).send(common.msgRoll(m, 'quake', queryResult[0][0]), file=discord.File("nowQuakeImages.png"))
                            else:
                                await self.get_guild(int(queryResult[0][0])).get_channel(int(channelResult[0][1])).send(common.msgRoll(m, 'quake', queryResult[0][0]))
                        index += 1
            # END FOR
intents = discord.Intents.default()
intents.message_content = True
# intents.manage_events = True
client = MyClient(intents=intents)
client.run(token.TOKEN)