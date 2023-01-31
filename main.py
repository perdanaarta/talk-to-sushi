from discord import Intents, Activity
from discord.ext import commands

import discord

import config
from logger import logger

class TalkToSushi(commands.Bot):
    """
    A weak Discord Talk to Speech
    """
    def __init__(self):
        super().__init__(intents=Intents.all(),
                         help_command=None,
                         command_prefix="<|not a goddamn placeholder|>")
        

    def run(self):
        logger.info("Starting bot")
        
        super().run(config.DISCORD_BOT_TOKEN, reconnect=True, log_handler=None)

        
    async def on_ready(self):
        await self.load_extension('cogs')
        try:
            await self.change_presence(
                activity=Activity(name=config.ACTIVITY_NAME,
                                  type=config.ACTIVITY_TYPE)
            )
        except: pass
        logger.info(f"Connected to Discord (latency: {self.latency*1000:,.0f} ms).")
        logger.info(f"{config.BOT_NAME} ready.")


    async def on_error(self, err, *args, **kwargs):
        raise 


    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)


def main():
    bot = TalkToSushi()
    bot.run()


if __name__ == '__main__':
    main()