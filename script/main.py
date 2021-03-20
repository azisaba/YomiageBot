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

token = sys.argv[1]
print("token: {0}".format(token))

# init status
status = status.Status(joined=False,channel_id="",voice_channel_id="",playing=False)
# message queue
message_queue = list()
# Instantiates a client
client = texttospeech.TextToSpeechClient()
# discord
bot = discord.Client()

# generate voice
def generate(message,file_name):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=message)
    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    # jp = ja-JP en= en-US
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    with open(file_name, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "{0}"'.format(file_name))

@bot.event
async def on_message(message):
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
            if status.joined == True:
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
                status.channel_id = text_channel.id
                status.voice_channel_id = voice_channel.id
                # connect
                await voice_channel.connect()
                status.joined = True
            return
        elif args[0] == "dc":
            # had joined
            if status.joined == False:
                await message.channel.send(':boom:エラー: 接続されていません')
                return
            if not message.channel.id == status.channel_id:
                return
            user = message.author
            text_channel = message.channel
            # get voice channel
            voice_channel = user.voice.channel
            if not voice_channel.id == status.voice_channel_id:
                await message.channel.send(':boom:エラー: VoiceChannelに接続してください')
                return
            vc = message.guild.voice_client
            status.joined = False
            status.playing = False
            await vc.disconnect()
            await text_channel.send('切断しました')
        return
    # channel
    if message.channel.id == status.channel_id:
        # has joined
        if status.joined == False:
            return
        message_queue.append(message.content)

# queue
def message_queue_task():
    global message_queue
    global bot
    global status
    while True:
        # has joined
        if status.joined == False:
            continue

        for message in message_queue[:]:
            while status.playing:
                time.sleep(1)
            # get voice channel
            voice_channel = bot.get_channel(status.voice_channel_id)
            # get voice client
            vc = voice_channel.guild.voice_client
            # generate
            generate(message, 'voice.mp3')
            # player
            vc.play(discord.FFmpegPCMAudio("voice.mp3"))
            status.playing = True
            while vc.is_playing():
                time.sleep(1)
            status.playing = False
            message_queue.remove(message)
        time.sleep(1)

thread = threading.Thread(target=message_queue_task)
thread.start()
# run
bot.run(token)