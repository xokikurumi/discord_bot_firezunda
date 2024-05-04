import discord
import re
import emoji
# pip install emoji

from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree
from common import logger
from common import dice
from common import common
# from API import earthQuek
from discord.ext import commands
from discord.ext import tasks
from constants import token
from googletrans import Translator
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

        if(isLang(message.content)):
            if message.author.bot:
                # マイクラbot,v1除外
                if not(message.author.id == 1066346686127026236 or message.author.id == 986560084891041892):
                    tr = Translator()
                    result = tr.translate(message.content,src='en',dest='ja').text
                    result = result.replace('：', ':')
# 正規表現を使用し、絵文字を削除する
                    result = re.sub(':[0-9a-zA-Z]:','',result)
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

    async def on_reaction_add(self, reaction, user):
        logger.info_reaction(reaction, user, reaction.message.content)

    async def on_reaction_remove(self, reaction, user):
        logger.info_reaction(reaction, user, reaction.message.content)
    # @tasks.loop(seconds=1)
    # async def earthQuek(self):
    #     # 地震/津波速報
    #     result = earthQuek.getInfomation(self)
    #     for txt in result:
    #         # 文字列を2000文字前後(改行コード毎計算)毎にデータを成形
    #         msgs = common.msgSplit(txt)
    #         for msg in msgs:
    #             # self.get_guild(999999).get_channel(99999).send("内容")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True
client = MyClient(intents=intents)
client.run(token.TOKEN)