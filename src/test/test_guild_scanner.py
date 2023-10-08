import pytest
from unittest.mock import patch
from bot.guild_scanner import GuildScanner, AlreadyScanningError, AlreadyQueuedError, GuildScanningRecord
from bot.memory_store import KarmaMemoryStore


class MockKarmaBot():
    def __init__(self) -> None:
        self.store = KarmaMemoryStore()

class MockKarmaBotContext:
    def __init__(self, guild):
        self.guild = guild
        self.bot = MockKarmaBot()

class MockGuild:
    def __init__(self, id):
        self.id = id
        self.channels = []

class MockTextChannel:
    async def history(self):
        return [x for x in range(100)]

@pytest.fixture
def guild_scanner():
    return GuildScanner()


def test_already_scanning_error():
    sr = GuildScanningRecord(total_channels=4, current_channel=0)
    e = AlreadyScanningError(sr)
    assert e.scanning_record == sr

def test_is_scanning_guild(guild_scanner):
    guild_id = 123
    assert not guild_scanner.is_scanning_guild(guild_id)

    guild_scanner.active_scanning_guilds[guild_id] = None
    assert guild_scanner.is_scanning_guild(guild_id)

def test_is_in_queue(guild_scanner):
    guild_id = 123
    assert not guild_scanner.is_in_queue(guild_id)

    guild_scanner.queue[guild_id] = None
    assert guild_scanner.is_in_queue(guild_id)

def test_add_to_queue(guild_scanner):
    guild_id = 123
    ctx = MockKarmaBotContext(MockGuild(guild_id))

    # Test adding to an empty queue
    guild_scanner.add_to_queue(guild_id, ctx)
    assert guild_scanner.is_in_queue(guild_id)

    # Test adding to an already queued guild
    with pytest.raises(AlreadyQueuedError):
        guild_scanner.add_to_queue(guild_id, ctx)

@pytest.mark.asyncio
async def test_scan_guild_empty(guild_scanner):
    assert not guild_scanner.queue
    await guild_scanner.scan_guild()
    assert not guild_scanner.queue

@pytest.mark.asyncio
async def test_scan_guild(guild_scanner):
    # Mock a context and guild
    guild_id = 123
    ctx = MockKarmaBotContext(MockGuild(guild_id))
    await ctx.bot.store.open()
    
    # Add a guild to the queue
    guild_scanner.add_to_queue(guild_id, ctx)
    
    # Test scanning the guild
    await guild_scanner.scan_guild()
    assert not guild_scanner.is_in_queue(guild_id)
    assert not guild_scanner.is_scanning_guild(guild_id)

    await ctx.bot.store.close()

# @pytest.mark.asyncio
# @patch('builtins.isinstance')
# async def test_count_guild_karma(guild_scanner):
#     # Mock a context and guild
#     guild_id = 123
#     ctx = MockKarmaBotContext(MockGuild(guild_id))

#     # Add some mock text channels to the guild
#     ctx.guild.channels = [MockTextChannel() for _ in range(3)]

#     # Test counting guild karma
#     guild_scanner.active_scanning_guilds[guild_id] = GuildScanningRecord(total_channels=0, current_channel=0)
#     with patch('discord.TextChannel') as mtc:
#         mtc.return_value = MockTextChannel
#         guild_karma = await guild_scanner.count_guild_karma(ctx)
#     assert isinstance(guild_karma, dict)
#     assert guild_id in guild_scanner.active_scanning_guilds
#     assert guild_scanner.active_scanning_guilds[guild_id].total_channels == 3
#     assert guild_scanner.active_scanning_guilds[guild_id].current_channel == 0
