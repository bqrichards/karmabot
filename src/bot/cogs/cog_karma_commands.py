from typing import Optional
from discord.ext import commands

from bot.bot import KarmaBot
from bot.karma_command import karma_command
from bot.leaderboard_command import leaderboard_command


class KarmaBotCommandsCog(commands.Cog):
    def __init__(self, bot: KarmaBot):
        self.bot = bot

    @commands.command()
    async def karma(self, ctx: commands.Context, member_name: Optional[str] = None):
        await karma_command(ctx, self.bot.store, member_name)


    @commands.command()
    async def leaderboard(self, ctx: commands.Context, member_count = 10):
        await leaderboard_command(ctx, self.bot.store, member_count)


async def setup(bot: KarmaBot):
    await bot.add_cog(KarmaBotCommandsCog(bot))
