from dataclasses import dataclass
from discord.ext.commands import Cog, Bot, Context
import discord
import os
import re

from main import logger
from . wrapper import TalkToSpeechWrapper, VoiceConfig
from . dictionary import languages

@dataclass
class InputMessage:
    user: str
    text: str
    config: VoiceConfig


class GuildPlayer:
    def __init__(self, guild: discord.Guild, voice: discord.VoiceClient) -> None:
        self.guild = guild
        self.voice = voice
        self.queue = []
        self.playing = False
        self.audio_path = os.path.join(os.path.dirname(__file__), f"../../../.temp/{self.guild.id}.wav")

    def play(self, msg):
        self.queue.append(msg)
        if not self.playing:
            self.__advance()

    def __advance(self):
        try:
            msg: InputMessage = self.queue.pop()
        except IndexError:
            os.remove(self.audio_path)
            self.playing = False
            return
        
        tts = TalkToSpeechWrapper()
        tts.synthesize_speech(msg.text, msg.config).save(self.audio_path)
        logger.info(f"<{msg.user}> Saying: {msg.text}")
        self.__playback()

    def __playback(self):
        self.playing = True
        try:
            self.voice.play(discord.FFmpegPCMAudio(
                source = self.audio_path,
                options = '-loglevel warning'
            ),
            after=lambda _: self.__advance())

        except Exception as e:
            logger.error(e)


class GuildPlayerManager:
    instances = {}

    @classmethod
    async def get(cls, guild: discord.Guild, voice: discord.VoiceClient = None) -> GuildPlayer:
        if guild.id in cls.instances:
            return cls.instances[guild.id]

        if voice is None:
            return None
        else:
            try:
                cls.instances[guild.id] = GuildPlayer(guild, voice)
                return cls.instances[guild.id]
            except:
                return None
            
    @classmethod
    async def destroy(cls, guild: discord.Guild) -> None:
        try:
            await guild.voice_client.disconnect()
        except Exception as e:
            # logger.error(e)
            pass

        try:
            del cls.instances[guild.id]
        except Exception as e:
            logger.error(e)


class ttsCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener('on_voice_state_update')
    async def voice_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        # Clean instance if bot disconnected
        if member.id == self.bot.application_id and after.channel is None:
            await GuildPlayerManager.destroy(guild)
        
        # Try to disconnect if there's no member in voice channel
        try:
            if not member.bot and after.channel != guild.voice_client.channel:
                if not [m for m in before.channel.members if not m.bot]:
                    await guild.voice_client.disconnect()
        except: pass

    @Cog.listener('on_message')
    async def on_message(self, msg: discord.Message):
        if not msg.author.bot:
            ctx: Context = await self.bot.get_context(msg, cls=Context)

        if msg.content.startswith(";"):
            await self.process_command(ctx)

    async def process_command(self, ctx: Context):
        if not ctx.message.author.voice:
            await ctx.send('User is not in accessible voice channel!')
            return

        try:
            try:
                voice = await ctx.author.voice.channel.connect()
            except:
                voice = discord.utils.get(self.bot.voice_clients, guild=ctx.author.guild)
            player = await GuildPlayerManager.get(ctx.guild, voice)

        except Exception as e:
            logger.error(e)
            await ctx.send('Cannot connect to voice channel!')
            return
        
        input = await self.process_message(ctx.message)
        if input == None:
            return

        try:
            player.play(input)
        except Exception as e:
            logger.error(e)

    async def process_message(self, message: discord.Message) -> InputMessage:
        clean_msg = re.sub(r'<.+?>', '', message.content.strip(';').strip())
        if clean_msg == "":
            return None

        split_msg = [m.lstrip().rstrip() for m in clean_msg.split(';')]
        text = None
        config = VoiceConfig()
        
        if len(split_msg) < 2:
            text = " ".join(split_msg)

        else:
            for i, msg in enumerate(split_msg):
                if msg in languages:
                    config.lang = msg

                elif msg in ['male', 'female']:
                    config.gender = msg

                else:
                    text =  " ".join(split_msg[i:])
                    break
        
        return InputMessage(message.author, text, config)
    
async def setup(bot):
    await bot.add_cog(ttsCog(bot))