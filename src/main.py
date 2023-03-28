import os
import pathlib
import discord
from discord.ext.commands import Bot

import config
from utils.logger import logger

class ArtaBot(Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents.all(),
            help_command=None,
            command_prefix="$"
        )

    def run(self) -> None:
        super().run(config.DISCORD_BOT_TOKEN, reconnect=True, log_handler=None)

    async def load_cogs(self):
        logger.info("Loading cogs...")
        ignore_list = []
        cog_dir = pathlib.Path(os.path.join(config.SRC_DIR, "./cogs"))
        for cog in cog_dir.iterdir():
            if "__" not in cog.name and cog.name not in ignore_list:
                try:
                    await self.load_extension(f"cogs.{cog.name}.{cog.name}")
                    logger.info(f"[{cog.name}] cog loaded.")
                except Exception as e:
                    logger.warning(e)
        
    async def on_ready(self):
        await self.load_cogs()
        try:
            await self.change_presence(
                activity=discord.Activity(name=config.ACTIVITY_NAME, type=config.ACTIVITY_TYPE)
            )
        except: pass
        logger.info(f"Connected to Discord (latency: {self.latency*1000:,.0f} ms).")
        logger.info(f"{config.BOT_NAME} ready.")


def main():
    bot = ArtaBot()
    bot.run()


if __name__ == '__main__':
    main()