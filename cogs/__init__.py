from .tts.tts import ttsCog
from .gpt.gpt import gptCog

async def setup(bot):
    await bot.add_cog(ttsCog(bot))
    await bot.add_cog(gptCog(bot))
    # print("Done")