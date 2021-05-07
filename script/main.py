# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Main
#   Date: 2021/3/19
########################

import sys
from google.cloud import texttospeech
import discord
import copy
import asyncio
import status
import time
import threading
import re
import voicegenerator
import message as message_data

token = sys.argv[1]
print("token: {0}".format(token))

# init status dict <id(str), status(Status.py)>
status_list = dict()
# message queue <message.py>
message_queue = list()

# Instantiates a client
client = texttospeech.TextToSpeechClient()
# discord
bot = discord.Client()

# remove url from str
def remove_url(msg):
    return re.sub(r'^https?:\/\/.*[\r\n]*', '', msg, flags=re.MULTILINE)

@bot.event
async def on_message(message):
    # Status check
    guild = message.guild
    guild_status = status.Status(joined=False,guild_id=guild.id,channel_id="",voice_channel_id="",playing=False)
    if guild.id in status_list:
        guild_status = status_list[guild.id]
    else:
        status_list[guild.id] = guild_status

    # bot
    if message.author.bot:
        return
    # args length
    if len(message.content) < 1:
        return
    # startWith
    if message.content[0] == "^":
        args = (copy.copy(message.content[1:])).split()
        # args length
        if len(args) < 1:
            return
        if args[0] == "con":
            # had joined
            if guild_status.joined == True:
                await message.channel.send(':boom:エラー: すでに参加しています')
                return
            # connect
            user = message.author
            # voice channel that user connected
            voice_channel = user.voice.channel
            # text channel happen event
            text_channel = message.channel

            # only play music if user is in a voice channel
            if voice_channel != None:
                await message.channel.send('読み上げを開始します '+ text_channel.name)
                # insert
                guild_status.channel_id = text_channel.id
                guild_status.voice_channel_id = voice_channel.id
                # connect
                await voice_channel.connect()
                guild_status.joined = True
            return
        elif args[0] == "dc":
            # had joined
            if guild_status.joined == False:
                await message.channel.send(':boom:エラー: 接続されていません')
                return
            if not message.channel.id == guild_status.channel_id:
                return
            user = message.author
            text_channel = message.channel
            # get voice channel
            voice_channel = user.voice.channel
            if not voice_channel.id == guild_status.voice_channel_id:
                await message.channel.send(':boom:エラー: VoiceChannelに接続してください')
                return
            vc = message.guild.voice_client
            guild_status.joined = False
            guild_status.playing = False
            await vc.disconnect()
            await text_channel.send('切断しました')
        return
    # channel
    if message.channel.id == guild_status.channel_id:
        # has joined
        if guild_status.joined == False:
            return
        
        msg = message.clean_content
        msg = remove_url(msg)
        # len check
        if len(msg) <= 0:
            return
        msg_data = message_data.Message(message=msg, guild_id=guild_status.guild_id)
        message_queue.append(msg_data)

# queue
def message_queue_task():
    global message_queue
    global bot
    global status
    global client

    while True:
        for message in message_queue[:]:
            # status
            guild_status = status_list[message.guild_id]
            # status check
            if guild_status.joined == False:
                message_queue.remove(message)
                return
            while guild_status.playing:
                time.sleep(1)
            # get voice client
            vc = bot.get_guild(message.guild_id).voice_client
            # logger
            print("message: {0}".format(message.message))
            # generate
            voicegenerator.generate(client,message.message, 'voice.mp3')
            
            try:
                # player
                vc.play(discord.FFmpegPCMAudio("voice.mp3"))
                # play
                guild_status.playing = True
                while vc.is_playing():
                    time.sleep(1)
                guild_status.playing = False
            except ClientException as ce:
                vc.stop()
                guild_status.playing = False

            message_queue.remove(message)
        time.sleep(1)

thread = threading.Thread(target=message_queue_task)
thread.start()
# run
bot.run(token)