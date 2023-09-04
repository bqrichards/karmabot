import asyncio
from dataclasses import dataclass
import logging
import janus
from discord import TextChannel

from bot.bot import KarmaBotContext


@dataclass
class GuildScanningRecord:
    total_channels: int
    """The total number of text channels to scan"""

    current_channel: int
    """The current channel being scanned"""


class AlreadyScanningError(Exception):
    """Error raised when guild is already being scanned when attempting to add to queue"""

    def __init__(self, scanning_record: GuildScanningRecord):
        self.scanning_record = scanning_record


class AlreadyQueuedError(Exception):
    """Error raised when guild is already in queue when attempting to add to queue"""

    def __init__(self, amount_ahead: int):
        self.amount_ahead = amount_ahead


class GuildScanner:
    def __init__(self):
        self.logger = logging.getLogger(__class__.__name__)

        self.queue: janus.AsyncQueue[KarmaBotContext] = janus.Queue().async_q
        """Queue of contexts of guilds to be scanned"""

        self.queue_ids: set[int] = set()
        """IDs of guilds in the queue"""

        self.active_scanning_guilds: dict[int, GuildScanningRecord] = dict()
        """Dictionary of guilds being actively scanned"""
    
    def is_scanning_guild(self, guild_id: int) -> bool:
        return guild_id in self.active_scanning_guilds

    def is_in_queue(self, guild_id: int) -> bool:
        return guild_id in self.queue_ids
    
    async def add_to_queue(self, guild_id: int, ctx: KarmaBotContext):
        if self.is_scanning_guild(guild_id):
            scanning_record = self.active_scanning_guilds[guild_id]
            raise AlreadyScanningError(scanning_record=scanning_record)
        elif self.is_in_queue(guild_id):
            # TODO Get amount ahead in queue
            amount_ahead = -1
            raise AlreadyQueuedError(amount_ahead=amount_ahead)
        else:
            # Add guild to scanning queue
            await self.queue.put(ctx)
            self.queue_ids.add(guild_id)        

    async def scan_guild(self):
        if self.queue.empty():
            return
        
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
            guild_karma: dict[int, int] = await self.count_guild_karma(ctx)
            
            await ctx.bot.store.set_guild_karma(guild_id, guild_karma)

            self.logger.debug(f'Done scanning guild {guild_id} -> {guild_karma}')

            self.active_scanning_guilds.pop(guild_id)

        self.queue.task_done()

    async def count_guild_karma(self, ctx: KarmaBotContext) -> dict[int, int]:
        if ctx.guild is None:
            return dict()
        
        guild_id = ctx.guild.id

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

        return guild_karma
