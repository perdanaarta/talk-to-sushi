import re
import discord
from discord.ext.commands import Bot, Cog, Context

from engine.text_to_speech import TextToSpeech, Dictionary
from main import config, logger
from .player import PlayerManager, Player


class TTSCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener('on_voice_state_update')
    async def voice_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        # Clean instance if bot disconnected
        if member.id == self.bot.application_id and after.channel is None:
            await PlayerManager.destroy(guild)

        # Try to disconnect if there's no member in voice channel
        try:
            if not member.bot and after.channel != guild.voice_client.channel:
                if not [m for m in before.channel.members if not m.bot]:
                    await guild.voice_client.disconnect()
        except:
            pass

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

        player = await self.__get_player(ctx)
        tts = await self.__get_text_to_speech(ctx)

        if player is None:
            return

        player.add_to_queue(ctx.author, tts)
        player.play()

    async def __get_player(self, ctx: Context):
        player = await PlayerManager.get(ctx.guild)
        if player is None:
            try:
                voice = discord.utils.get(self.bot.voice_clients, guild=ctx.author.guild)
                if voice == None:
                    voice = await ctx.author.voice.channel.connect()

                player = await PlayerManager.get(ctx.guild, voice)

            except Exception as e:
                await ctx.send('Cannot connect to voice channel!')
                logger.error(e)

        return player

    async def __get_text_to_speech(self, ctx: Context):
        clean_msg = re.sub(r'<.+?>', '', ctx.message.content.strip(';').strip())
        if clean_msg == "":
            return None

        split_msg = [m.lstrip().rstrip() for m in clean_msg.split(';')]
        text = None
        language = 'en'
        gender = None

        if len(split_msg) < 2:
            text = " ".join(split_msg)

        else:
            for i, msg in enumerate(split_msg):
                if msg in Dictionary.languages:
                    language = msg

                elif msg in ['male', 'female']:
                    gender = msg

                else:
                    text = " ".join(split_msg[i:])
                    break

        return TextToSpeech(text=text, language=language, gender=gender)

async def setup(bot):
    await bot.add_cog(TTSCog(bot))
