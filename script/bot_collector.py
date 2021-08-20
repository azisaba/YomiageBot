# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: BotCollector
#   Date: 2021/8/16
########################

from dataclasses import dataclass
from listener_bot import ListenerBot


@dataclass
class BotCollector:
    """Class for Collecting bot info"""
    listener_bot: ListenerBot
    speaker_bot_list: list

    def get_speakers(self):
        return self.speaker_bot_list

    def get_listener(self):
        return self.listener_bot

    def get_speaker(self, client_id):
        for _sb in self.speaker_bot_list:
            if _sb.discord_client.user.id == client_id:
                return _sb
        return None
