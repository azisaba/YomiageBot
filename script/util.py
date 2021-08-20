# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Util
#   Date: 2021/8/16
########################

import re


# detect url and remove
def remove_url(message):
    return re.sub(r'^https?:\/\/.*[\r\n]*', '', message, flags=re.MULTILINE)
