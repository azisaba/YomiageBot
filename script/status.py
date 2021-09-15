# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Status
#   Date: 2021/3/19
########################

import dataclasses


@dataclasses.dataclass
class Status:
    """
    - client_id: client.user.id
    - guild_id: guild.id
    - channel_id: text_channel.id
    - voice_channel_id: voice_channel.id
    """
    client_id: str
    guild_id: str
    channel_id: str
    voice_channel_id: str
