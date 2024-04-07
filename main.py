import discord
import re
from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree
from common import logger
from common import dice
from common import common
from API import earthQuek
from discord.ext import commands
from discord.ext import tasks
from constants import token
from googletrans import Translator
# pip install googletrans==4.0.0rc1

# 英語のみ反応させる
# 他の言語は気が向いたら
def isLang(msg):
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
        '^\\(\\)>',
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
    
    return result

class MyClient(discord.Client):



    async def on_ready(self):
        print('Logged on as', self.user)
        self.earthQuek.start()

    # 通常のメッセージが送信された場合
    async def on_message(self, message):
        # don't respond to ourselves
        logger.info(message, message.content)
        if message.author == self.user:
            return

        # ダイスチェック
        if not(message.author.id == 1208286469953953833 or message.author.id == 1226387089566994555):
            if dice.isDice(message.content):
                diceLog = dice.getResultDice(message.content)
                if(diceLog["ok"]):
                    await message.channel.send(diceLog["text"])
                    return
# <：ZND：1166641599674056725>
        if(isLang(message.content)):
            if not(message.author.id == 1066346686127026236 or message.author.id == 986560084891041892 or message.author.id == 1208286469953953833):
                tr = Translator()
                result = tr.translate(message.content,src='en',dest='ja').text
                result = result.replace('：', ':')
                await message.channel.send(result)
                print(result)
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
     # 地震/津波速報
     result = earthQuek.getInfomation(self)
     # ギルド・チャンネル・メンション一覧を取得
     channels = earthQuek.getChannels(self)
     if len(result) > 0:
         for serverData in channels:
            if serverData[2] == 'everyone':
                await self.get_guild(int(serverData[0])).get_channel(int(serverData[1])).send("@everyone 災害情報")
            else:
                await self.get_guild(int(serverData[0])).get_channel(int(serverData[1])).send(serverData[2] + " 災害情報")

            for txt in result:
                 # 文字列を2000文字前後(改行コード毎計算)毎にデータを成形
                sendData = None
                first = True
                dataCnt = 0
                for text2 in txt:
                    if first:
                        sendData = discord.Embed(title=text2[0], description=text2[1], color= 0xff0000)
                        first = False
                    else:
                        if (1< dataCnt and dataCnt < 9):

                            sendData.add_field(name=text2[0], value=text2[1], inline = True)
                        else: 
                            sendData.add_field(name=text2[1], value='', inline = False)
                    dataCnt = dataCnt + 1
                await self.get_guild(int(serverData[0])).get_channel(int(serverData[1])).send(embed=sendData)

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(token.TOKEN)