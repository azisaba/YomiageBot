# -*- coding: utf-8 -*-
########################
#   Project: Yomiage
#   Author: testusuke
#   Class: message
#   Date: 2021/3/29
########################

import dataclasses

@dataclasses.dataclass
class Message:
    message: str
    guild_id: str