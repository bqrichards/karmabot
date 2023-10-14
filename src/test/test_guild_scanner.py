import pytest
from bot.guild_scanner import GuildScanner, AlreadyScanningError, AlreadyQueuedError, GuildScanningRecord
from test.mocks import create_mock_text_channel, mock_guild, mock_karma_bot_context


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
    ctx = mock_karma_bot_context(mock_guild(guild_id))

    # Test adding to an empty queue
    guild_scanner.add_to_queue(guild_id, ctx)
    assert guild_scanner.is_in_queue(guild_id)

    # Test adding to an already queued guild
    with pytest.raises(AlreadyQueuedError):
        guild_scanner.add_to_queue(guild_id, ctx)

def test_add_to_queue_already_scanning(guild_scanner):
    guild_id = 123
    ctx = mock_karma_bot_context(mock_guild(guild_id))

    guild_scanner.active_scanning_guilds[guild_id] = ctx

    # Test adding to an already scanning guild
    with pytest.raises(AlreadyScanningError):
        guild_scanner.add_to_queue(guild_id, ctx)

@pytest.mark.asyncio
async def test_scan_guild_empty(guild_scanner):
    assert not guild_scanner.queue
    await guild_scanner.scan_guild()
    assert not guild_scanner.queue

@pytest.mark.asyncio
async def test_scan_guild_no_guild(guild_scanner):
    # Mock a context and guild
    guild_id = 123
    ctx = mock_karma_bot_context(None)
    await ctx.bot.store.open()
    
    # Add a guild to the queue
    guild_scanner.add_to_queue(guild_id, ctx)
    
    # Test scanning the guild
    await guild_scanner.scan_guild()

    assert not guild_id in guild_scanner.active_scanning_guilds

    await ctx.bot.store.close()

@pytest.mark.asyncio
async def test_scan_guild(guild_scanner):
    # Mock a context and guild
    guild_id = 123
    ctx = mock_karma_bot_context(mock_guild(guild_id))
    await ctx.bot.store.open()
    
    # Add a guild to the queue
    guild_scanner.add_to_queue(guild_id, ctx)
    
    # Add some mock text channels to the guild
    ctx.guild.channels = [create_mock_text_channel(), create_mock_text_channel()]

    # Test scanning the guild
    await guild_scanner.scan_guild()
    assert not guild_scanner.is_in_queue(guild_id)
    assert not guild_scanner.is_scanning_guild(guild_id)

    await ctx.bot.store.close()

@pytest.mark.asyncio
async def test_count_guild_karma_guild_none(guild_scanner):
    # Mock a context and guild
    ctx = mock_karma_bot_context(None)
    guild_karma = await guild_scanner.count_guild_karma(ctx)
    assert guild_karma == {}

@pytest.mark.asyncio
async def test_count_guild_karma(guild_scanner):
    # Mock a context and guild
    guild_id = 123
    ctx = mock_karma_bot_context(mock_guild(guild_id))

    # Add some mock text channels to the guild
    ctx.guild.channels = [create_mock_text_channel(), create_mock_text_channel()]

    # Test counting guild karma
    guild_scanner.active_scanning_guilds[guild_id] = GuildScanningRecord(total_channels=2, current_channel=0)
    guild_karma = await guild_scanner.count_guild_karma(ctx)
    assert isinstance(guild_karma, dict)
    assert guild_id in guild_scanner.active_scanning_guilds
    assert guild_scanner.active_scanning_guilds[guild_id].total_channels == 2
    assert guild_scanner.active_scanning_guilds[guild_id].current_channel == 2
    assert guild_karma == {456: 6}
