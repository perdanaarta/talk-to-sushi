from discord.ext.commands import Bot, Cog, Context
from discord import app_commands, FFmpegPCMAudio
import discord

from dataclasses import dataclass

from main import logger
from . wrapper import TalkToSpeechWrapper, VoiceConfig
from . dictionary import languages
import re, asyncio, os

@dataclass
class InputMessage:
    user: str
    text: str
    config: VoiceConfig


class GuildPlayer():
    def __init__(self, guild: discord.Guild, voice: discord.VoiceClient):
        self.guild = guild
        self.voice = voice
        self.queue = []
        self.playing = False
        self.audio_path = os.path.join(os.path.dirname(__file__), f"../../../.temp/{self.guild.id}.wav")
        
    def play(self, input):
        self.queue.append(input)

        if not self.playing:
            self.advance()

    def advance(self):
        try:
            msg: InputMessage = self.queue.pop()
        except IndexError:
            os.remove(self.audio_path)
            self.playing = False
            return
        
        tts = TalkToSpeechWrapper()
        tts.synthesize_speech(msg.text, msg.config).save(self.audio_path)

        logger.info(f"<{msg.user}> Saying: {msg.text}")
        self.playback()

    def playback(self):
        self.playing = True
        try:
            self.voice.play(FFmpegPCMAudio(
                source = self.audio_path,
                options = '-loglevel panic'
            ),
            after=lambda _: self.advance())

        except Exception as e:
            logger.error(e)


class GuildPlayerManager():
    def __init__(self) -> None:
        self.instances = {}

    async def create(self, guild: discord.Guild, voice: discord.VoiceClient) -> GuildPlayer:
        try:
            self.instances[guild.id] = GuildPlayer(guild, voice)
            return self.instances[guild.id]
        except Exception as e:
            logger.error(e)
            return None

    async def get(self, guild: discord.Guild) -> GuildPlayer:
        try:
            return self.instances[guild.id]
        except:
            return None

    async def destroy(self, guild: discord.Guild) -> None:
        try:
            await guild.voice_client.disconnect()
        except:
            pass

        try:
            del self.instances[guild.id]
        except Exception as e:
            logger.warn(e)


class ttsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.player_manager = GuildPlayerManager()

    @Cog.listener('on_voice_state_update')
    async def voice_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        # Clean instance if bot disconnected
        if member.id == self.bot.application_id and after.channel is None:
            await self.player_manager.destroy(guild)
        
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


    # @app_commands.command(name='default_voice')
    # @app_commands.option('gender', choices=['Male', 'Female'])
    # async def set_default_voice(self, ctx: Context, gender: str):
    #     saved_data[ctx.author.id] = gender.lower()
    #     await ctx.respond(f'Default gender set to {gender.lower()}')


    # @app_commands.command(name='tts')
    # async def slash_tts(self, msg):
    #     print(msg)


    async def process_command(self, ctx: Context):
        """Core talk to speech"""
        if not ctx.message.author.voice:
            await ctx.send('User is not in accessible voice channel!')
            return
        
        input = await self.process_message(ctx.message)
        if input == None:
            return

        # if ctx.author.id in saved_data and 'gender' not in msg.params:
        #     msg.params['gender'] = saved_data[ctx.author.id]

        try:
            player = await self.player_manager.get(ctx.guild)
            if player is None:
                player = await self.player_manager.create(
                    ctx.guild,
                    await ctx.author.voice.channel.connect()
                )
        except Exception as e:
            logger.error(e)
            await ctx.send('Cannot connect to voice channel!')
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