import discord
from discord.ext import commands, tasks


class Handlers(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.update_stats.start()

    @property
    def category(self):
        return ["None"]

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await self.hyena.topgg.post_guild_count()
            print(f"Posted server count ({self.hyena.topgg.guild_count})")
        except Exception as e:
            print("Failed to post server count\n{}: {}".format(type(e).__name__, e))


def setup(hyena):
    hyena.add_cog(Handlers(hyena))
