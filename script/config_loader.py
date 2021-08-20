# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: ConfigLoader
#   Date: 2021/8/15
########################

import os
import yaml
import traceback


class ConfigLoader:

    def __init__(self, path, config):
        # check file
        if not os.path.exists(path):
            try:
                raise ValueError("cannot find configuration file")
            except ValueError:
                traceback.print_exc()
        # open
        try:
            with open(path) as file:
                obj = yaml.safe_load(file)
                # listener
                config.set_listener(token=obj["listener_token"])
                # speaker
                for token in obj["speaker_token"]:
                    config.add_token(token=token)
        except ValueError:
            traceback.print_exc()
