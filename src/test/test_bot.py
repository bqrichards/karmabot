# import discord
import discord
import pytest
from unittest.mock import MagicMock, Mock, AsyncMock, patch
# from discord.ext import commands

from bot.bot import KarmaBot
from bot.config import KarmaConfig
from bot.memory_store import KarmaMemoryStore
from bot.store import KarmaStore
from test.mocks import create_mock_message, mock_guild

# Define a fixture to create a KarmaBot instance for testing
@pytest.fixture
@patch('bot.bot.super')
def karma_bot(patched_super):
    config = KarmaConfig(upvote_emojis=['👍'], downvote_emojis=['👇'], command_prefix='!')
    store = KarmaMemoryStore()
    bot = KarmaBot(config, store)
    return bot

# Test cases for KarmaBot methods
def test_reaction_is_upvote(karma_bot):
    emoji = discord.PartialEmoji(name='👍')
    assert karma_bot.reaction_is_upvote(emoji)

def test_reaction_is_downvote(karma_bot):
    emoji = discord.PartialEmoji(name='👇')
    assert karma_bot.reaction_is_downvote(emoji)

def test_unknown_reaction(karma_bot):
    emoji = discord.PartialEmoji(name='👎')
    assert not karma_bot.reaction_is_upvote(emoji)
    assert not karma_bot.reaction_is_downvote(emoji)

@pytest.mark.asyncio
async def test_on_ready(karma_bot):
    with patch('bot.bot.KarmaBot.user'):
        await karma_bot.on_ready()  # Simply test if it runs without errors

@pytest.mark.asyncio
async def test_setup_hook_no_cogs(karma_bot):
    with patch('discord.ext.commands.Bot.load_extension') as load_ext, patch('os.listdir'):
        karma_bot.store = Mock(spec=KarmaStore)

        await karma_bot.setup_hook()
        
        # Setup hook opens the store
        assert karma_bot.store.open.called

        # Doesn't load any extensions since listdir returns []
        assert not load_ext.called

@pytest.mark.asyncio
async def test_setup_hook_cogs(karma_bot):
    with patch('discord.ext.commands.Bot.load_extension') as load_ext, patch('os.listdir') as listdir:
        listdir.return_value = ['test.py']
        karma_bot.store = Mock(spec=KarmaStore)

        await karma_bot.setup_hook()
        
        # Setup hook opens the store
        assert karma_bot.store.open.called

        load_ext.assert_called_once_with('bot.cogs.test')

@pytest.mark.asyncio
async def test_get_message_sender_id_no_guildid(karma_bot):
    payload = Mock(name='discord.RawReactionActionEvent', spec=['guild_id', 'channel_id', 'message_id'])
    payload.guild_id = None
    payload.channel_id = 456
    payload.message_id = 789

    sender_id = await karma_bot.get_message_sender_id(payload)
    assert sender_id == None

@pytest.mark.asyncio
async def test_get_message_sender_id_no_guild(karma_bot):
    payload = Mock(name='discord.RawReactionActionEvent', spec=['guild_id', 'channel_id', 'message_id'])
    payload.guild_id = 123
    payload.channel_id = 456
    payload.message_id = 789

    guild = None
    karma_bot.get_guild = Mock(return_value=guild)

    sender_id = await karma_bot.get_message_sender_id(payload)
    assert sender_id == None

@pytest.mark.asyncio
async def test_get_message_no_channel(karma_bot):
    payload = Mock(name='discord.RawReactionActionEvent', spec=['guild_id', 'channel_id', 'message_id'])
    payload.guild_id = 123
    payload.channel_id = 456
    payload.message_id = 789

    # Mock the necessary Discord objects and methods
    guild = mock_guild(payload.guild_id)
    karma_bot.get_guild = Mock(return_value=guild)
    guild.get_channel = Mock(return_value=None)

    sender_id = await karma_bot.get_message_sender_id(payload)
    assert sender_id == None

@pytest.mark.asyncio
async def test_get_message_sender_id(karma_bot):
    payload = Mock(name='discord.RawReactionActionEvent', spec=['guild_id', 'channel_id', 'message_id'])
    payload.guild_id = 123
    payload.channel_id = 456
    payload.message_id = 789
    author_id = 999

    # Mock the necessary Discord objects and methods
    message = create_mock_message(author_id)

    partial_message = AsyncMock(spec=discord.PartialMessage)
    partial_message.fetch.return_value = message

    channel = AsyncMock(spec=discord.channel.TextChannel)
    channel.id = payload.channel_id
    channel.get_partial_message.return_value = partial_message

    guild = Mock(spec=discord.Guild)
    guild.id = payload.guild_id
    guild.get_channel = Mock(return_value=channel)
    karma_bot.get_guild = Mock(return_value=guild)

    sender_id = await karma_bot.get_message_sender_id(payload)
    assert sender_id == 999

@pytest.mark.asyncio
@patch('bot.bot.super', AsyncMock)
async def test_close(karma_bot):
    karma_bot.store = Mock(spec=KarmaStore)
    await karma_bot.close()

    # Closing bot calls close on the store
    assert karma_bot.store.close.called
