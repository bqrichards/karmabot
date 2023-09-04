import logging
from typing import Any, Coroutine
from discord.ext import commands, tasks

from bot.bot import KarmaBot
from bot.bot import KarmaBotContext
from bot.guild_scanner import AlreadyScanningError, AlreadyQueuedError, GuildScanner


class KarmaBotGuildScannerCog(commands.Cog):
    def __init__(self, bot: KarmaBot):
        self.bot = bot
        self.logger = logging.getLogger(__class__.__name__)
        self.guild_scanner = GuildScanner()
        self.scan_next_guild.start()
    
    def cog_unload(self) -> Coroutine[Any, Any, None]:
        self.scan_next_guild.cancel()
        return super().cog_unload()

    @commands.command()
    async def scan(self, ctx: KarmaBotContext):
        # Get user id
        if not ctx.guild:
            self.logger.debug('Guild could not be found on message')
            return
        
        guild_id = ctx.guild.id

        try:
            self.guild_scanner.add_to_queue(guild_id, ctx)
            await ctx.send('This guild has be added to the scanning queue')
        except AlreadyScanningError as e:
            await ctx.send(f'This guild is already being scanned. Progress: {e.scanning_record.current_channel}/{e.scanning_record.total_channels} channels')
        except AlreadyQueuedError as e:
            await ctx.send(f'This guild is already in the queue. Amount ahead in queue: {e.amount_ahead}')            

    @tasks.loop(seconds=1)
    async def scan_next_guild(self):
        await self.guild_scanner.scan_guild()

    @scan_next_guild.before_loop
    async def before_scan_guilds(self):
        await self.bot.wait_until_ready()


async def setup(bot: KarmaBot):
    await bot.add_cog(KarmaBotGuildScannerCog(bot))
