import os
import discord
from main import config, logger
from engine.text_to_speech import TextToSpeech


class Player():
    def __init__(self, guild: discord.Guild, voice: discord.VoiceClient):
        self.guild = guild
        self.voice = voice
        self.queue = []
        self.playing = False
        self.audio_file = os.path.join(config.SRC_DIR, f"../.temp/{self.guild.id}.wav")

    def add_to_queue(self, user: discord.User, tts: TextToSpeech):
        self.queue.append({
            'user': user,
            'tts': tts
        })

    def __advance(self):
        try:
            item = self.queue.pop()
            user: discord.User = item['user']
            tts: TextToSpeech = item['tts']

        except IndexError:
            self.playing = False
            return

        except Exception as e:
            logger.error(e)
            return

        tts.convert()
        tts.save(self.audio_file)

        logger.info(f"<{user.global_name}> Saying: {tts.text}")
        self.__playback()

    def __playback(self):
        self.playing = True
        try:
            self.voice.play(
                discord.FFmpegPCMAudio(
                    source=self.audio_file,
                    options='-loglevel panic'
                ),
                after=lambda _: self.__advance()
            )

        except Exception as e:
            self.playing = False
            logger.error(e)

    def play(self):
        if not self.playing:
            self.__advance()

class PlayerManager:
    instances = {}

    @classmethod
    def __create_instance(cls, guild_id: str, voice: discord.VoiceClient):
        cls.instances[guild_id] = voice
        return voice

    @classmethod
    def __delete_instance(cls, guild_id: str):
        del cls.instances[guild_id]

    @classmethod
    def __get_instance(cls, guild_id: str):
        try:
            return cls.instances[guild_id]
        except:
            return None
    
    @classmethod
    async def get(cls, guild: discord.Guild, voice: discord.VoiceClient = None) -> Player:
        instance = cls.__get_instance(guild.id)

        if instance is None:
            if voice is None:
                logger.warn(f"Guild: {guild.name}. Voice Channel not specified")
                return

            try:
                instance = cls.__create_instance(guild.id, Player(guild, voice))
            except Exception as e:
                logger.error(e)

        return instance

    @classmethod
    async def destroy(cls, guild: discord.Guild):
        try:
            await guild.voice_client.disconnect()
        except Exception as e:
            logger.warn(e)

        cls.__delete_instance(guild.id)

