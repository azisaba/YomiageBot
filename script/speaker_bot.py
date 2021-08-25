# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: SpeakerBot
#   Date: 2021/8/15
########################

from discord import Client, FFmpegPCMAudio, ClientException
from google.cloud import texttospeech
import asyncio
from queue import Queue, Empty
from threading import Thread
import time
from voice_generator import VoiceGenerator


class SpeakerBot:

    def __init__(self, token, bm, loop, working_path):
        """
        SpeakerBot(token, mm, bm)

        Initializing speaker bot
        Argument:
        - token: String
        - bm: BotManager(bot_manager.py)
        - loop: event loop
        - working_path: working directory path
        :param token, bm, loop, working_path:
        """
        self.info("Lunching SpeakerBot...")
        # instance status
        self.enabled = True
        # init
        self.google_client = texttospeech.TextToSpeechClient()
        self.discord_client = Client()
        self.bm = bm
        self.vg = VoiceGenerator(self.google_client, working_path="{0}/{1}".format(working_path, self.__hash__()))
        # prepare Queue
        self.queue = Queue()
        # speaker init
        self.st = Thread(target=self.speak_thread)
        self.st.start()
        # run
        loop.create_task(self.discord_client.start(token))
        self.info("launched")

    def add_message(self, message):
        """
        add_message(ml)

        Add list of messages to local list.
        Argument:
        - message: Message
        :param message:
        """
        self.queue.put(message)

    def speak_thread(self):
        while self.enabled:
            try:
                msg = self.queue.get(block=True, timeout=3)
                guild = self.discord_client.get_guild(msg.guild_id)
                if guild is None:
                    continue
                vc = guild.voice_client
                if vc is None:
                    continue
                # generate
                mp3_path = self.vg.generate(msg.message, "voice.mp3")
                vc.play(FFmpegPCMAudio(mp3_path))
                # block
                while vc.is_playing():
                    time.sleep(0.5)
            except Empty:
                # Queue Exception
                continue
            except ClientException:
                # Audio Exception
                self.info("raise ClientException in speak_thread")
                continue

    def shutdown(self):
        # thread
        self.info("shutdown thread...")
        self.enabled = False
        self.st.join()
        self.info("done")
        # client
        self.info("shutdown client...")
        loop = asyncio.get_event_loop()
        loop.create_task(self.discord_client.close())
        self.info("done")

    def info(self, message):
        print("{0}@{1}: {2}".format("SpeakerBot", self.__hash__(), message))
