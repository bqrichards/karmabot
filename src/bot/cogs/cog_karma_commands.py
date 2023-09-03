import logging
from typing import Optional
from discord.ext import commands

from bot.bot import KarmaBot, KarmaBotContext
from bot.commands.karma_command import karma_command
from bot.commands.leaderboard_command import leaderboard_command


class KarmaBotCommandsCog(commands.Cog):
    def __init__(self, bot: KarmaBot):
        self.bot = bot
        self.logger = logging.getLogger(__class__.__name__)

    @commands.command()
    async def karma(self, ctx: KarmaBotContext, member_name: Optional[str] = None):
        await karma_command(ctx, member_name)

    @commands.command()
    async def leaderboard(self, ctx: KarmaBotContext, member_count = 10):
        await leaderboard_command(ctx, member_count)


async def setup(bot: KarmaBot):
    await bot.add_cog(KarmaBotCommandsCog(bot))
