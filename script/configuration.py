# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Configuration
#   Date: 2021/8/15
########################

from dataclasses import dataclass


@dataclass
class Configuration:
    """Class for memorizing list of tokens"""
    listener_token: str
    speaker_token_list: list

    def add_token(self, token):
        self.speaker_token_list.append(token)

    def set_listener(self, token):
        self.listener_token = str(token)
