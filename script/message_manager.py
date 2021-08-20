# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: MessageManager
#   Date: 2021/8/16
########################

class MessageManager:

    def __init__(self, bm):
        self.bm = bm
        pass

    def add(self, message):
        """
        add(Message)

        Add message to collection.
        :param message:
        """
        # TODO Statusを参照しどのインスタンスに投げればいいか判断して、インスタンス内のQueueに追加する
        status = self.bm.get_status(channel_id=message.channel_id)
        if status is None:
            return
        sb = self.bm.bc.get_speaker(client_id=status.client_id)
        if sb is None:
            return
        sb.add_message(message=message)
