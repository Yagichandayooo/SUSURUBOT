import discord
import pickle
import sys
import numpy as np
import logging
import settings
from apiclient.discovery import build

#discoのログ
logging.basicConfig(level=logging.INFO)
# discobotのトークン
TOKEN = settings.TK


# 接続に必要なオブジェクトを生成
client = discord.Client()

#youtubeAPI関連
API_KEY= settings.AP
def get_videos_search(keyword):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    youtube_query = youtube.search().list(q=keyword, part='id,snippet', maxResults=1)
    youtube_res = youtube_query.execute()
    return youtube_res.get('items', [])

#SUSURUのデータをまとめてるところ
SUSURU_DB = []
ramen_list = []
with open("NEWSUSURU.pickle", mode="rb") as f:
    SUSURU_DB = pickle.load(f)
    count = len(SUSURU_DB)
    print(count)
    for num in range(count):
        st = SUSURU_DB[num]['description']
        fd = st.find('【本日のラーメン情報】')
        fd2 = st.find('【本日のお店情報】')
        shop_list = []
        shop = ''
        if  fd == -1 and fd2 == -1:
            shop = ''
        elif fd == -1 or fd2 == -1:
            if fd == -1:
                fd = fd2
            for t in SUSURU_DB[num]['description'][fd:]:
                if t == '■'or t =='★' or t == '☆':
                    break
                shop += t
        title = SUSURU_DB[num]['title']
        ramen_list.append(title +"\n" + shop)

ModeFlag = 0

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    await client.change_presence(activity=discord.Game(name="!susuruで検索モード", type=1))#ステータスバーの管理

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    global ModeFlag
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    if message.content == '!exit':
        await message.channel.send('see you;;')
        sys.exit()
#キーワードを検索して当てはまるリストを上から5件表示
    if ModeFlag == 1:
        word = message.content
        ModeFlag = 0
        count = 0
        kensaku = [s for s in ramen_list if word in s]
        for five in range(5):
            result = get_videos_search(kensaku[five])
            for item in result:
                url = 'https://www.youtube.com/watch?v=' + item['id']['videoId']
                await message.channel.send(kensaku[five] + url + "\n")
        
#ラーメン検索モードにきりかえ
    if message.content == '!susuru':
        ModeFlag = 1
        await message.channel.send('検索したいキーワードを入力してください！！')
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)