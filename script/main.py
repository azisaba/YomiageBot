# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Main
#   Date: 2021/8/15
########################

import sys
import os
import shutil
import asyncio
import signal
from configuration import Configuration
from config_loader import ConfigLoader
from bot_manager import BotManager


def clash_handler(signum, frame):
    # request shutdown
    bot_manager.shutdown_all()
    loop.stop()
    print("see you")
    exit(1)


if __name__ == "__main__":
    # event loop
    loop = asyncio.get_event_loop()
    # signal
    signal.signal(signal.SIGINT, clash_handler)
    # working directory
    working_path = os.path.abspath(sys.argv[1])
    print("working directory: {0}".format(working_path))
    # make data directory
    _data_directory = "{0}/data".format(working_path)
    if os.path.exists(_data_directory):
        shutil.rmtree(_data_directory)
        print("remove old data folder")
    os.mkdir(_data_directory)
    print("make data folder")
    # load configuration
    config = Configuration("", [])
    _config_path = "{0}/config.yml".format(working_path)
    _config_loader = ConfigLoader(path=_config_path, config=config)
    print("Listener:\n{0}\nSpeaker:\n{1}".format(config.listener_token, config.speaker_token_list))
    # lunch bot
    bot_manager = BotManager(config=config, loop=loop, working_path=_data_directory)

    # run loop
    loop.run_forever()
