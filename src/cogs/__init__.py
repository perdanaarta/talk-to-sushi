from .tts.tts import ttsCog
from .gpt.gpt import gptCog
from .battleship.battleship import BattleshipCog

async def setup(bot):
    await bot.add_cog(ttsCog(bot))
    await bot.add_cog(gptCog(bot))
    await bot.add_cog(BattleshipCog(bot))