import asyncio
from dataclasses import dataclass
import logging
from typing import Any, Coroutine
from discord import TextChannel
from discord.ext import commands, tasks
import janus

from bot.bot import KarmaBot
from bot.bot import KarmaBotContext


@dataclass
class GuildScanningRecord:
    total_channels: int
    """The total number of text channels to scan"""

    current_channel: int
    """The current channel being scanned"""


class KarmaBotGuildScannerCog(commands.Cog):
    def __init__(self, bot: KarmaBot):
        self.bot = bot
        self.logger = logging.getLogger(__class__.__name__)

        # TODO Move guild queue logic to seperate class
        self.queue: janus.AsyncQueue[KarmaBotContext] = janus.Queue().async_q
        """Queue of contexts of guilds to be scanned"""

        self.queue_ids: set[int] = set()
        """IDs of guilds in the queue"""

        self.active_scanning_guilds: dict[int, GuildScanningRecord] = dict()
        """Dictionary of guilds being actively scanned"""

        self.scan_guilds.start()
    
    def cog_unload(self) -> Coroutine[Any, Any, None]:
        self.scan_guilds.cancel()
        return super().cog_unload()

    @commands.command()
    async def scan(self, ctx: KarmaBotContext):
        # Get user id
        if not ctx.guild:
            self.logger.debug('Guild could not be found on message')
            return
        
        guild_id = ctx.guild.id

        # Check if already scanning
        guild_scanning = guild_id in self.active_scanning_guilds
        guild_in_queue = guild_id in self.queue_ids

        if guild_scanning:
            scanning_record = self.active_scanning_guilds[guild_id]
            await ctx.send(f'This guild is already being scanned. Progress: {scanning_record.current_channel}/{scanning_record.total_channels} channels')
        elif guild_in_queue:
            # TODO Get amount ahead in queue
            amount_ahead = -1
            await ctx.send(f'This guild is already in the queue. Amount ahead in queue: {amount_ahead}')
        else:
            # Add guild to scanning queue
            await self.queue.put(ctx)
            self.queue_ids.add(guild_id)
            await ctx.send('This guild has be added to the scanning queue')

    @tasks.loop(seconds=1)
    async def scan_guilds(self):
        if not self.queue.empty():
            ctx = await self.queue.get()

            if ctx.guild is None:
                self.logger.warn('ctx.guild is none')
            else:
                guild_id = ctx.guild.id
                self.queue_ids.remove(guild_id)

                # Mark this guild as being scanned
                self.active_scanning_guilds[guild_id] = GuildScanningRecord(total_channels=0, current_channel=0)

                self.logger.debug(f'Begin scanning guild: {guild_id}')

                # Scan all text channels for reactions
                text_channels = [channel for channel in ctx.guild.channels if isinstance(channel, TextChannel)]
                self.active_scanning_guilds[guild_id].total_channels = len(text_channels)
                guild_karma: dict[int, int] = dict()
                for channel in text_channels:
                    self.active_scanning_guilds[guild_id].current_channel += 1
                    self.logger.debug(self.active_scanning_guilds[guild_id])
                    await asyncio.sleep(5) # FIXME remove after adding feature

                    async for message in channel.history(limit=200): # TODO remove limit
                        author = message.author.id
                        message_karma = 0
                        for reaction in message.reactions:                                
                            if reaction.emoji in ctx.bot.config.upvote_emojis:
                                message_karma += 1
                            elif reaction.emoji in ctx.bot.config.downvote_emojis:
                                message_karma -= 1
                        old_karma = guild_karma.get(author, 0)
                        guild_karma[author] = old_karma + message_karma
                
                await ctx.bot.store.set_guild_karma(guild_id, guild_karma)

                self.logger.debug(f'Done scanning guild {guild_id} -> {guild_karma}')

                self.active_scanning_guilds.pop(guild_id)

            self.queue.task_done()

    @scan_guilds.before_loop
    async def before_scan_guilds(self):
        await self.bot.wait_until_ready()


async def setup(bot: KarmaBot):
    await bot.add_cog(KarmaBotGuildScannerCog(bot))
