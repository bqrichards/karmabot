from collections import OrderedDict
from dataclasses import dataclass
import logging
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

        self.queue: OrderedDict[int, KarmaBotContext] = OrderedDict()
        """Queue of contexts of guilds to be scanned"""

        self.active_scanning_guilds: dict[int, GuildScanningRecord] = dict()
        """Dictionary of guilds being actively scanned"""
    
    def is_scanning_guild(self, guild_id: int) -> bool:
        return guild_id in self.active_scanning_guilds

    def is_in_queue(self, guild_id: int) -> bool:
        return guild_id in self.queue
    
    def add_to_queue(self, guild_id: int, ctx: KarmaBotContext):
        if self.is_scanning_guild(guild_id):
            scanning_record = self.active_scanning_guilds[guild_id]
            raise AlreadyScanningError(scanning_record=scanning_record)
        elif self.is_in_queue(guild_id):
            # Get amount ahead in queue
            amount_ahead = -1
            for queued_guild_index, queued_guild_id in enumerate(self.queue):
                if queued_guild_id == guild_id:
                    amount_ahead = queued_guild_index
            raise AlreadyQueuedError(amount_ahead=amount_ahead)
        else:
            # Add guild to scanning queue
            self.queue[guild_id] = ctx

    async def scan_guild(self):
        # Check if queue is empty
        if not self.queue:
            return
        
        guild_id, ctx = self.queue.popitem(last=False)

        if ctx.guild is None:
            return

        # Mark this guild as being scanned
        self.active_scanning_guilds[guild_id] = GuildScanningRecord(total_channels=0, current_channel=0)

        self.logger.debug(f'Begin scanning guild: {guild_id}')

        # Scan all text channels for reactions
        text_channels = [channel for channel in ctx.guild.channels if isinstance(channel, TextChannel)]
        self.active_scanning_guilds[guild_id].total_channels = len(text_channels)
        guild_karma: dict[int, int] = await self.count_guild_karma(ctx)
        
        await ctx.bot.store.set_guild_karma(guild_id, guild_karma)

        self.logger.debug(f'Done scanning guild {guild_id} -> {guild_karma}')

        self.active_scanning_guilds.pop(guild_id) # Remove from active list

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

            async for message in channel.history(limit=10000):
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
