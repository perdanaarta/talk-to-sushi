import os
from discord import Guild, VoiceClient, FFmpegPCMAudio
from .dictionary import languages
from .wrapper import TalkToSpeechWrapper
from main import logger

instances = {}
saved_data = {}

class TTSMessage():
    def __init__(self, msg: str) -> None:
        self.params, self.text = self.split_msg(msg)
    
    def split_msg(self, message) -> tuple:
        msg = []
        for m in message.split(';'):
            msg.append(m.lstrip().rstrip())
        
        params, text = {}, ""

        if len(msg) < 2:
            text += " ".join(msg)

            return params, text

        else:
            for i, m in enumerate(msg):
                m = m.lstrip().rstrip()

                if m in languages:
                    params['lang'] = m

                elif m in ['male', 'female']:
                    params['gender'] = m

                else:
                    text += " ".join(msg[i:])
                    break
                
            return params, text


class GuildPlayer():
    def __init__(self, guild: Guild, voice: VoiceClient):
        self.guild = guild
        self.voice = voice
        self.queue = []
        self.playing = False
        
    def play(self, message):
        self.queue.append(message)

        if not self.playing:
            self.advance()

    def advance(self):
        try:
            msg = self.queue.pop()
        except IndexError:
            os.remove(f'{self.guild.id}.wav')
            self.playing = False
            return
        
        TalkToSpeechWrapper(msg).save(f'{self.guild.id}.wav')
        logger.info(f"{msg.user} saying: {msg.text}")
        self.playback()

    def playback(self):
        self.playing = True
        try:
            self.voice.play(FFmpegPCMAudio(
                source = f'{self.guild.id}.wav',
                options = '-loglevel panic'
            ),
            after=lambda _: self.advance())

        except: raise
