from gtts import gTTS
from google.cloud.texttospeech import TextToSpeechClient, SynthesisInput, AudioConfig, AudioEncoding, VoiceSelectionParams

from . import base
from .dictionary import languages, wavenets, wavenet_support, accents
from main import config

import os, json

gcloud = None
class TalkToSpeechWrapper():
    """:params:
    
    'lang' = Language of the voice
    'gender' = Gender of the voice
    'rate' = Speaking rate of the voice
    'pitch' = Pitch for the voice
    """
    def __init__(self, msg: base.Message):
        self.gcloud = self.connect_gcloud()        

        self.text = msg.text
        self.audio = self.talk_to_speech(msg)


    def connect_gcloud(self):
        global gcloud
        
        if gcloud is None:
            try:
                gcloud = TextToSpeechClient.from_service_account_file(config.GCLOUD_API_KEY)
            except:
                gcloud = None

        return gcloud

            
    def talk_to_speech(self, msg: base.Message) -> bytes:
        if self.gcloud == None:
            return self.gtts(msg)

        msg = self.is_wavenet(msg)

        if msg.lang in wavenet_support:
            return self.gcs(msg)
        else:
            return self.gtts(msg)


    def is_wavenet(self, msg: base.Message):
        def get_wavenet(g):
            for wn in wavenets[msg.lang]:
                if wn['gender'].lower() == g:
                    return wn['name']

        if msg.lang in wavenet_support and msg.gender is not None:
            msg.lang = wavenet_support[msg.lang]
            msg.name = get_wavenet(msg.gender)

        elif msg.lang in accents:
            msg.lang = wavenet_support[msg.lang]
            msg.name = get_wavenet('female')

        return msg
        

    def gtts(self, msg: base.Message) -> bytes:
        """Transform text into audio bytes using gtts"""
        text = msg.text
        lang = "en" if msg.lang is None else msg.lang

        def process(text: str):
            for decoded in (gTTS(text, 'com', lang).stream()): 
                return(decoded)
        try: 
            audio_data, line = b'', ""
            for word in text.split(" "):
                if len(line) + 1 + len(word) > 100:
                    audio_data += process(line)
                    line = ""
                    line += word

                else:
                    line += " " + word

            audio_data = audio_data + process(line)
            return audio_data
        
        except:
            return process('please dont abuse me')
    
    def gcs(self, msg: base.Message) -> bytes:
        """Transform text into audio bytes using gcs text to speech"""

        text = msg.text
        lang = msg.lang
        name = msg.name
        rate = 1.0 if msg.rate is None else msg.rate
        pitch = 0.0 if msg.pitch is None else msg.pitch

        text_input = SynthesisInput(text=text)
        audio_config = AudioConfig(
            audio_encoding = AudioEncoding.LINEAR16,
            speaking_rate = rate,
            pitch = pitch
        )

        voice_params = VoiceSelectionParams(
            language_code = lang,
            name = name
        )

        response = self.gcloud.synthesize_speech(input=text_input,
                                                 voice=voice_params,
                                                 audio_config=audio_config)
        
        return response.audio_content
    
    def save(self, path):
        """Save into audio file"""
        with open(path, "wb") as out:
            out.write(self.audio)
