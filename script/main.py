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

token = sys.argv[1]
print("token: {0}".format(token))

# Instantiates a client
client = texttospeech.TextToSpeechClient()
# discord
_joined = False
bot = discord.Client()

# generate voice
def generate(message,file_name):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=message)
    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
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
            if _joined == True:
                await message.channel.send(':boom:エラー: すでに参加しています')
                return
            # connect
            user = message.author
            voice_channel = user.voice.voice_channel
            text_channel = message.channel
            _joined = False
            # only play music if user is in a voice channel
            if voice_channel != None:
                await message.channel.send('読み上げを開始します '+ text_channel.name)
                _message_channel = text_channel
                _vc = await client.join_voice_channel(voice_channel)
                _joined = True
            return
        elif args[0] == "dc":
            # had joined
            if _joined == False:
                await message.channel.send(':boom:エラー: 接続されていません')
                return
            user = message.author
            text_channel = message.channel
            await _vc.disconnect()
            await text_channel.send('切断しました')
        return
    # channel
    if message.channel == _message_channel:
        # has joined
        if not  _joined == True:
            return
        # generate
        generate(message.content, 'voice.mp3')
        # player
        player = vc.create_ffmpeg_player('voice.mp3', after=lambda: print('done'))
        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        player.stop()

# run
bot.run(token)