from discord.ext.commands import Bot, Cog, Context
from discord import app_commands
import discord

from . import base
from . dictionary import languages
from . core import GuildPlayer, instances, saved_data
import re, asyncio


class ttsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def create_instance(self, guild: discord.Guild, voice: discord.VoiceClient) -> GuildPlayer | None:
        try:
            instances[guild.id] = GuildPlayer(guild, voice)
            return instances[guild.id]
        except:
            return None

    async def get_instance(self, guild: discord.Guild) -> GuildPlayer | None:
        try:
            return instances[guild.id]
        except KeyError:
            return None
    
    async def clean_instance(self, guild: discord.Guild) -> None:
        try:
            del instances[guild.id]
        except KeyError:
            pass

    @Cog.listener('on_voice_state_update')
    async def voice_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        # Clean instance if bot disconnected
        if member.id == self.bot.application_id and after.channel is None:
                await self.clean_instance(guild)
        
        # Try to disconnect if there's no member in voice channel
        try:
            if not member.bot and after.channel != guild.voice_client.channel:
                await asyncio.sleep(5)
                if not [m for m in before.channel.members if not m.bot]:
                    await guild.voice_client.disconnect()
        except: pass

    @Cog.listener('on_message')
    async def text_tts(self, msg: discord.Message):
        if not msg.author.bot:
            ctx: Context = await self.bot.get_context(msg, cls=Context)

        if msg.content.startswith(";"):
            await self.talk_to_speech(ctx)


    # @app_commands.command(name='default_voice')
    # @app_commands.option('gender', choices=['Male', 'Female'])
    # async def set_default_voice(self, ctx: Context, gender: str):
    #     saved_data[ctx.author.id] = gender.lower()
    #     await ctx.respond(f'Default gender set to {gender.lower()}')


    # @app_commands.command(name='tts')
    # async def slash_tts(self, msg):
    #     print(msg)

    def split_message(self, message: base.Message):
        split_msg = [m.lstrip().rstrip() for m in message.text.split(';')]
        
        if len(split_msg) < 2:
            message.text = " ".join(split_msg)
            return message

        else:
            for i, msg in enumerate(split_msg):
                if msg in languages:
                    message.lang = msg

                elif msg in ['male', 'female']:
                    message.gender = msg

                else:
                    message.text =  " ".join(split_msg[i:])
                    break

            return message

    async def talk_to_speech(self, ctx: Context):
        """Core talk to speech"""
        if not ctx.message.author.voice:
            await ctx.send('User is not in accessible voice channel!')
            return
        
        msg = re.sub(r'<.+?>', '', ctx.message.content.strip(';').strip())
        if msg == "": return

        msg = self.split_message(base.Message(user = ctx.message.author,
                                              text = msg))

        # if ctx.author.id in saved_data and 'gender' not in msg.params:
        #     msg.params['gender'] = saved_data[ctx.author.id]

        try:
            tts = await self.get_instance(ctx.guild)
            if tts is None:
                tts = await self.create_instance(
                    ctx.guild,
                    await ctx.author.voice.channel.connect()
                )
        except:
            await ctx.send('Cannot connect to voice channel!')
            return

        tts.play(msg)