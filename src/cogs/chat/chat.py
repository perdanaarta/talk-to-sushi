from discord.ext.commands import Cog, Bot, command
from discord import app_commands
import discord
import asyncio

from main import logger
from main import config

from . import base
from . import completion
from .utils import close_thread, is_last_message_stale, discord_message_to_message
from .completion import generate_completion_response, process_response


class ChatCog(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        
    @Cog.listener("on_ready")
    async def on_ready(self):
        example_convos = completion.BOT_EXAMPLE_CONVOS
        completion.BOT_NAME = self.bot.user.name
        completion.BOT_EXAMPLE_CONVOS = []
        for c in example_convos:
            messages = []
            for m in c.messages:
                if m.user == "<bot>":
                    messages.append(base.Message(user=self.bot.user.name, text=m.text))
                else:
                    messages.append(m)
            completion.BOT_EXAMPLE_CONVOS.append(base.Conversation(messages=messages))

    @app_commands.command(name="chat", description="Start chatting with me!")
    async def chat_command(self, interaction: discord.Interaction, message: str):
        try:
            # only support creating thread in text channel
            if not isinstance(interaction.channel, discord.TextChannel):
                return

            # # block servers not in allow list
            if interaction.guild.id not in config.ALLOWED_SERVER_IDS:
                return

            user = interaction.user
            logger.info(f"Chat command by {user} {message[:20]}")
            try:
                embed = discord.Embed(
                    description=f"<@{user.id}> wants to chat! 💬",
                    color=discord.Color.green(),
                )
                embed.add_field(name=user.name, value=message)

                await interaction.response.send_message(embed=embed)
                response = await interaction.original_response()

            except Exception as e:
                logger.exception(e)
                await interaction.response.send_message(
                    f"Failed to start chat {str(e)}", ephemeral=True
                )
                return

            # create the thread
            thread: discord.Thread = await response.create_thread(
                name=f"{config.ACTIVE_THREAD_PREFIX} {user.name[:20]} - {message[:30]}",
                slowmode_delay=1,
                reason="gpt-bot",
                auto_archive_duration=60,
            )
            async with thread.typing():
                # fetch completion
                messages = [base.Message(user=user.name, text=message)]
                response_data = await generate_completion_response(
                    messages=messages, user=user
                )
                # send the result
                await process_response(
                    user=user, thread=thread, response_data=response_data
                )
                
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(
                f"Failed to start chat {str(e)}", ephemeral=True
            )
    
    @Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        try:
            # block servers not in allow list
            if message.guild.id not in config.ALLOWED_SERVER_IDS:
                return

            # ignore messages from the bot
            if message.author.id == self.bot.user.id:
                return

            # ignore messages not in a thread
            channel = message.channel
            if not isinstance(channel, discord.Thread):
                return

            # ignore threads not created by the bot
            thread = channel
            if thread.owner_id != self.bot.user.id:
                return

            # ignore threads that are archived locked or title is not what we want
            if (
                thread.archived
                or thread.locked
                or not thread.name.startswith(config.ACTIVE_THREAD_PREFIX)
            ):
                # ignore this thread
                return

            if thread.message_count > config.MAX_THREAD_MESSAGES:
                # too many messages, no longer going to reply
                await close_thread(thread=thread)
                return

            # wait a bit in case user has more messages
            if config.SECONDS_DELAY_RECEIVING_MSG > 0:
                await asyncio.sleep(config.SECONDS_DELAY_RECEIVING_MSG)
                if is_last_message_stale(
                    interaction_message=message,
                    last_message=thread.last_message,
                    bot_id=self.bot.user.id,
                ):
                    # there is another message, so ignore this one
                    return

            logger.info(
                f"Thread message to process - {message.author}: {message.content[:50]} - {thread.name} {thread.jump_url}"
            )

            channel_messages = [
                discord_message_to_message(message)
                async for message in thread.history(limit=config.MAX_THREAD_MESSAGES)
            ]
            channel_messages = [x for x in channel_messages if x is not None]
            channel_messages.reverse()

            # generate the response
            async with thread.typing():
                response_data = await generate_completion_response(
                    messages=channel_messages, user=message.author
                )

            if is_last_message_stale(
                interaction_message=message,
                last_message=thread.last_message,
                bot_id=self.bot.user.id,
            ):
                # there is another message and its not from us, so ignore this response
                return

            # send response
            await process_response(
                user=message.author, thread=thread, response_data=response_data
            )
        except Exception as e:
            logger.exception(e)

async def setup(bot):
    await bot.add_cog(ChatCog(bot))
