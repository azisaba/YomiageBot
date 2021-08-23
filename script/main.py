# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Main
#   Date: 2021/3/19
########################

import copy
import sys
import threading
import time
import re

from google.cloud import texttospeech
import discord
import yaml

import message as message_data
import status
import voicegenerator


class RepDict():
    def __init__(self):
        with open('dictionary.yml', 'r') as f:
            self.dictionary = yaml.safe_load(f)

        if self.dictionary is None:
            self.dictionary = dict()

    def save(self):
        with open('dictionary.yml', 'w') as f:
            yaml.safe_dump(self.dictionary, f)

    def add(self, word, pronunciation):
        self.dictionary[word] = pronunciation
        self.save()

    def remove(self, word):
        try:
            del self.dictionary[word]
            self.save()
            return True

        except KeyError:
            return False

    def replace(self, msg):
        for word, pronunciation in self.dictionary.items():
            msg = msg.replace(word, pronunciation)

        return msg


# remove url from str
def remove_url(msg):
    return re.sub(r'^https?:\/\/.*[\r\n]*', '', msg, flags=re.MULTILINE)


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

# dictionary
dictionary = RepDict()


@bot.event
async def on_message(message):
    global dictionary
    # Status check
    guild = message.guild
    guild_status = status.Status(joined=False, guild_id=guild.id, channel_id="", voice_channel_id="", playing=False)
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
            if guild_status.joined is True:
                await message.channel.send(':boom:エラー: すでに参加しています')
                return
            # connect
            user = message.author
            # voice channel that user connected
            voice_channel = user.voice.channel
            # text channel happen event
            text_channel = message.channel

            # only play music if user is in a voice channel
            if voice_channel is not None:
                await message.channel.send('読み上げを開始します ' + text_channel.name)
                # insert
                guild_status.channel_id = text_channel.id
                guild_status.voice_channel_id = voice_channel.id
                # connect
                await voice_channel.connect()
                guild_status.joined = True
            return

        elif args[0] == "dc":
            # had joined
            if guild_status.joined is False:
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

        elif args[0] == "ch":
            # had joined
            if guild_status.joined is False:
                await message.channel.send('VCに参加していません')
                return
            channel_name = guild.get_channel(guild_status.channel_id).name
            await message.channel.send('{0} に参加しています'.format(channel_name))

        elif args[0] == "dict":
            try:
                if args[1] == "add":
                    dictionary.add(*args[2:])
                    await message.channel.send('これからは {0} を {1} と読みます！'.format(*args[2:]))

                elif args[1] == "remove":
                    result = dictionary.remove(args[2])
                    if result is True:
                        await message.channel.send('{}を辞書から削除しました'.format(args[2]))
                    else:
                        await message.channel.send('{}は辞書に登録されていません！'.format(args[2]))

            except KeyError:
                await message.channel.send('構文エラーだと思われます。直してください。')

            return

        return
    # channel
    if message.channel.id == guild_status.channel_id:
        # has joined
        if guild_status.joined is False:
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
    global dictionary

    while True:
        for message in message_queue[:]:
            # status
            guild_status = status_list[message.guild_id]
            # status check
            if guild_status.joined is False:
                message_queue.remove(message)
                return
            while guild_status.playing:
                time.sleep(1)
            # get voice client
            vc = bot.get_guild(message.guild_id).voice_client
            # logger
            print("message: {0}".format(message.message))
            # replace with dictionary
            message.message = dictionary.replace(message.message)
            # generate
            voicegenerator.generate(client, message.message, 'voice.mp3')
            message_queue.remove(message)

            try:
                # player
                vc.play(discord.FFmpegPCMAudio("voice.mp3"))
                # play
                guild_status.playing = True
                while vc.is_playing():
                    time.sleep(1)
                guild_status.playing = False
            except:
                pass
        time.sleep(1)


thread = threading.Thread(target=message_queue_task)
thread.start()
# run
bot.run(token)
