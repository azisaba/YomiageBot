# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: ListenerBot
#   Date: 2021/8/16
########################

import discord
import asyncio
from copy import copy
from util import remove_url
from message import Message


class ListenerBot:

    def __init__(self, token, mm, bm, loop):
        """
        ListenerBot(token, mm, bm)

        Initializing Listener bot
        Argument:
        - token: String
        - mm: MessageManager(message_manager.py)
        - bm: BotManager(bot_manager.py)
        - loop: event loop
        :param token, mm, bm, loop:
        """
        self.info("Launching bot...")
        # init
        self.client = discord.Client()
        self.client.on_message = self.on_message
        self.mm = mm
        self.bm = bm
        # run
        loop.create_task(self.client.start(token))
        self.info("launched")

    async def on_message(self, message):
        # perm
        guild = message.guild
        text_channel = message.channel
        user = message.author
        # bot
        if user.bot:
            return
        # message length
        if len(message.content) < 1:
            return

        if message.content[0] == "^":
            args = copy(message.content[1:]).split()
            if len(args) < 1:
                return
            # Command
            if args[0] == "con":
                """Command for connecting to vc"""
                # user is joining to vc
                voice_state = user.voice
                if voice_state is None:
                    await text_channel.send(':boom:エラー: ボイスチャンネルに参加してください')
                    return
                voice_channel = voice_state.channel
                # bot has been joining vc
                if self.bm.is_tracked(vc_channel_id=voice_channel.id):
                    await text_channel.send(':boom:エラー: すでにこのVCに参加しています')
                    return
                # channel has been registered
                if self.bm.is_tracked(channel_id=text_channel.id):
                    await text_channel.send(':boom:エラー: すでにこのチャンネルは登録されています')
                    return

                self.bm.connect_request(guild_id=guild.id, channel_id=text_channel.id, vc_channel_id=voice_channel.id)

            elif args[0] == "dc":
                """Command of disconnecting from vc"""
                # user is joining to vc
                voice_state = user.voice
                if voice_state is None:
                    await text_channel.send(':boom:エラー: ボイスチャンネルに参加してください')
                    return
                voice_channel = voice_state.channel
                # channel has been registered
                if not self.bm.is_tracked(channel_id=text_channel.id, vc_channel_id=voice_channel.id):
                    await text_channel.send(':boom:エラー: 接続されていません')
                    return

                self.bm.disconnect_request(guild_id=guild.id, channel_id=text_channel.id,
                                           vc_channel_id=voice_channel.id)

            elif args[0] == "status":
                """Command for showing status"""
                _csl = self.bm.connectable_speaker_list(guild_id=guild.id)
                _asl = self.bm.available_speaker_list(guild_id=guild.id)
                # joined is True, else is False
                _speaker_condition_dict = dict()
                for _asb in _asl:
                    if _asb in _csl:
                        _speaker_condition_dict[_asb] = False
                    else:
                        _speaker_condition_dict[_asb] = True
                msg = ""
                for _key in _speaker_condition_dict.keys():
                    _value = _speaker_condition_dict.get(_key)
                    if _value:
                        msg += "{0} -> {1}\n".format(_key.discord_client.user.name, ":hot_face: 使用中")
                    else:
                        msg += "{0} -> {1}\n".format(_key.discord_client.user.name, ":white_check_mark: 利用可能")
                embed = discord.Embed(title='稼働状況', color=discord.Colour.blue())
                embed.add_field(name='List', value=msg, inline=False)
                await text_channel.send(embed=embed)

            elif args[0] == "setting":
                # TODO feature: 声の種類,速度,ピッチを変更可能にする
                pass

            elif args[0] == "help":
                embed = discord.Embed(
                    title=":question: ヘルプ",
                    description=
                    """
                    Command:
                     - ^con : 読み上げを開始します
                     - ^dc : 切断します
                     - ^status : ステータスを表示します
                     - ^help : ヘルプを表示します
                    """,
                    color=discord.Colour.green()
                )
                await text_channel.send(embed=embed)

            return

        else:
            """Format message and Package. And call add_message"""
            # format
            # remove mention
            msg = message.clean_content
            # remove url
            msg = remove_url(message=msg)

            # length
            if len(msg) <= 0:
                return
            msg_data = Message(message=msg, guild_id=guild.id, channel_id=text_channel.id)
            self.mm.add(msg_data)

    def shutdown(self):
        self.info("shutdown client...")
        loop = asyncio.get_event_loop()
        loop.create_task(self.client.close())
        self.info("done")

    def info(self, message):
        print("{0}@{1}: {2}".format("ListenerBot", self.__hash__(), message))
