# -*- coding: utf-8 -*-
########################
#   Project: Yomiage
#   Author: testusuke
#   Class: Status
#   Date: 2021/3/19
########################

import dataclasses


@dataclasses.dataclass
class Status:
    joined: bool
    guild_id: str
    channel_id: str
    voice_channel_id: str
    playing: bool
