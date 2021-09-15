# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: message
#   Date: 2021/3/29
########################

import dataclasses


@dataclasses.dataclass
class Message:
    """Class for having message and id"""
    message: str
    guild_id: str
    channel_id: str
