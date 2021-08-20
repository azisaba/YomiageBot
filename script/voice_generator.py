# -*- coding: utf-8 -*-
########################
#   Project: YomiageBot
#   Author: testusuke
#   Class: Main
#   Date: 2021/3/19
########################
from google.cloud import texttospeech
import os


class VoiceGenerator:

    def __init__(self, client, working_path):
        self.client = client
        self.working_path = working_path
        if not os.path.exists(self.working_path):
            os.mkdir(self.working_path)
            print("make folder {0}".format(self.working_path))

    # generate voice
    def generate(self, message, file_name):
        _formatted_name = "{0}/{1}".format(self.working_path, file_name)
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=message)
        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        # jp = ja-JP en= en-US
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=1.25
        )
        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        # The response's audio_content is binary.
        with open(_formatted_name, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
        return _formatted_name
