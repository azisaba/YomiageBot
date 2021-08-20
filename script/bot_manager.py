# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: BotManager
#   Date: 2021/8/15
########################

import asyncio
import copy
import random
from message_manager import MessageManager
from listener_bot import ListenerBot
from speaker_bot import SpeakerBot
from bot_collector import BotCollector
from status import Status


class BotManager:

    def __init__(self, config, loop, working_path):
        """
        Class for managing bot. for instance, connect vc and disconnect, receive message and collect.

        :param config: configuration for launching bot
        :param loop: event loop for bot, etc.
        :param working_path: working directory path(/parent_dir/data/)
        """
        # message manager
        self.mm = MessageManager(bm=self)
        # initialize bot
        self._lb = ListenerBot(token=config.listener_token, mm=self.mm, bm=self, loop=loop)
        _sb_list = list()
        for _t in config.speaker_token_list:
            _sb = SpeakerBot(token=_t, bm=self, loop=loop, working_path=working_path)
            _sb_list.append(_sb)
        # BotCollector
        self.bc = BotCollector(self._lb, _sb_list)
        # Status list
        self._status_list = list()

    def connect_request(self, guild_id, channel_id, vc_channel_id):
        # TODO 接続可能なBOTを探す,接続,登録,読み上げ開始 -> DONE
        loop = asyncio.get_event_loop()
        _lb_channel = self._lb.client.get_channel(channel_id)
        # check existing available bot
        _sbl = self.connectable_speaker_list(guild_id=guild_id)
        if len(_sbl) <= 0:
            loop.create_task(_lb_channel.send(':boom:エラー: 現在利用できるBotがありません'))
            return
        # TODO feature: connecting speaker bot with fewer connection
        # random connect
        _sb = _sbl[random.randrange(len(_sbl))]
        _sbc = _sb.discord_client
        _vc = _sbc.get_channel(vc_channel_id)
        loop.create_task(_vc.connect())
        """
        # is connected
        _sbg = _sbc.get_guild(guild_id)
        if _sbg is None:
            loop.create_task(_lb_channel.send(':boom:エラー: Guildの取得に失敗しました'))
            return
        if _sbg.voice_client is None:
            loop.create_task(_lb_channel.send(':boom:エラー: VCに接続できませんでした'))
            return
        """
        # register
        self._register_status(client_id=_sbc.user.id, channel_id=channel_id, vc_channel_id=vc_channel_id)
        loop.create_task(_lb_channel.send('{0}が読み上げを開始します {1}'.format(_sbc.user.name, _lb_channel.name)))

    def disconnect_request(self, guild_id, channel_id, vc_channel_id):
        # TODO Audioの停止, voice_clientの削除, disconnect, 削除 -> DONE
        # vc.stop() vc<-remove disconnect
        loop = asyncio.get_event_loop()
        _lb_channel = self._lb.client.get_channel(channel_id)

        _sbs = self.get_status(channel_id=channel_id, vc_channel_id=vc_channel_id)
        _sb = self.bc.get_speaker(client_id=_sbs.client_id)
        _sbc = _sb.discord_client
        _sbg = _sbc.get_guild(guild_id)
        if _sbg is None:
            loop.create_task(_lb_channel.send(':boom:エラー: Guildの取得に失敗しました'))
            return
        _vc = _sbg.voice_client
        if _vc is None:
            loop.create_task(_lb_channel.send(':boom:エラー: VoiceClientの取得に失敗しました'))
            return
        # stop
        if _vc.is_playing():
            _vc.stop()
        # disconnect
        loop.create_task(_vc.disconnect())
        # remove status
        self._unregister_status(client_id=_sbc.user.id, channel_id=channel_id, vc_channel_id=vc_channel_id)
        loop.create_task(_lb_channel.send('切断しました'))

    def _register_status(self, client_id, channel_id, vc_channel_id):
        guild = self._lb.client.get_channel(channel_id).guild
        status = Status(client_id=client_id, guild_id=guild.id, channel_id=channel_id, voice_channel_id=vc_channel_id)
        if status in self._status_list:
            return
        self._status_list.append(status)

    def _unregister_status(self, client_id, channel_id, vc_channel_id):
        guild = self._lb.client.get_channel(channel_id).guild
        status = Status(client_id=client_id, guild_id=guild.id, channel_id=channel_id, voice_channel_id=vc_channel_id)
        self._status_list.remove(status)

    def status_list(self):
        """Return copied List of Status"""
        return copy.copy(self._status_list)

    def get_status(self, channel_id=None, vc_channel_id=None):
        """

        :param channel_id:
        :param vc_channel_id:
        :return: if not find,return None
        """
        if channel_id is not None and vc_channel_id is None:
            for _s in self._status_list:
                if channel_id == _s.channel_id:
                    return _s

        elif channel_id is None and vc_channel_id is not None:
            for _s in self._status_list:
                if vc_channel_id == _s.voice_channel_id:
                    return _s

        elif channel_id is not None and vc_channel_id is not None:
            for _s in self._status_list:
                if channel_id == _s.channel_id and vc_channel_id == _s.voice_channel_id:
                    return _s
        return None

    def is_tracked(self, channel_id=None, vc_channel_id=None):
        if self.get_status(channel_id=channel_id, vc_channel_id=vc_channel_id) is None:
            return False
        else:
            return True

    def available_speaker_list(self, guild_id):
        """
        Get a list of available speaker bot.
        it's meaning that joined bot in guild.

        :param guild_id:
        :return List[SpeakerBot]:
        """
        # collect speaker client
        speaker_list = list()
        for _c in self.bc.get_speakers():
            # if speaker has joined to guild, return guild
            if not _c.discord_client.get_guild(guild_id) is None:
                speaker_list.append(_c)
        return speaker_list

    def connectable_speaker_list(self, guild_id):
        """
        Get a list of connectable speaker bot.
        it's meaning that bot is idling in guild.

        :param guild_id:
        :return List[SpeakerBot]:
        """
        # collect status
        guilds_status_list = list()
        channels = self._lb.client.get_guild(guild_id).text_channels
        for _s in self._status_list:
            _channel = self._lb.client.get_channel(_s.channel_id)
            if _channel in channels:
                guilds_status_list.append(_s)
        # collect client id
        guilds_speaker_list = list()
        for _s in guilds_status_list:
            _sb = self.bc.get_speaker(client_id=_s.client_id)
            guilds_speaker_list.append(_sb)
        # collect speaker client
        speaker_list = self.available_speaker_list(guild_id=guild_id)
        # compare
        _connectable_speaker_list = list()
        for _sb in speaker_list:
            if _sb not in guilds_speaker_list:
                _connectable_speaker_list.append(_sb)

        return _connectable_speaker_list

    def shutdown_all(self):
        # listener
        self.bc.listener_bot.shutdown()
        # speaker
        for c in self.bc.speaker_bot_list:
            c.shutdown()
