# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Util
#   Date: 2021/8/16
########################

import re
import yaml


# detect url and remove
def remove_url(message):
    return re.sub(r'^https?:\/\/.*[\r\n]*', '', message, flags=re.MULTILINE)

class RepDict:
    def __init__(self, dictionary_path):
        self.dictionary_path = dictionary_path
        with open(self.dictionary_path, 'r') as f:
            self.dictionary = yaml.safe_load(f)

        if self.dictionary is None:
            self.dictionary = dict()

    def save(self):
        with open(self.dictionary_path, 'w') as f:
            yaml.safe_dump(self.dictionary, f)

    def add(self, word, pronunciation):
        self.dictionary[word] = pronunciation
        self.save()

    def remove(self, word):
        try:
            del self.dictionary[word]
            self.save()
            return True

        except KeyError:
            return False

    def replace(self, msg):
        for word, pronunciation in self.dictionary.items():
            msg = msg.replace(word, pronunciation)

        return msg
