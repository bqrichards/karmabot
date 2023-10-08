from unittest.mock import Mock

import discord
from bot.bot import KarmaBot
from bot.config import KarmaConfig
from bot.memory_store import KarmaMemoryStore
from discord.ext import commands

class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

def create_mock_message(author_id: int):
    mock_upvote_reaction = Mock(name='discord.Reaction', spec=['emoji'])
    mock_upvote_reaction.emoji = '👍'

    mock_downvote_reaction = Mock(name='discord.Reaction', spec=['emoji'])
    mock_downvote_reaction.emoji = '👎'

    mock_message = Mock(name='discord.Message', spec=['author', 'reactions'])
    mock_message.author.id = author_id
    mock_message.reactions = [mock_upvote_reaction, mock_upvote_reaction, mock_downvote_reaction]

    return mock_message

def create_mock_text_channel():
    # Create mock text channels
    mock_text_channel = Mock(name='discord.TextChannel', spec=discord.TextChannel)
    mock_text_channel.history.return_value = AsyncIterator(create_mock_message(456) for _ in range(3))
    return mock_text_channel

def mock_karma_bot():
    m = Mock(spec=KarmaBot)
    m.store = KarmaMemoryStore()
    m.config = KarmaConfig(upvote_emojis=['👍'], downvote_emojis=['👎'], command_prefix='?')
    return m

def mock_guild(id: int):
    m = Mock(spec=discord.Guild)
    m.id = id
    return m

def mock_karma_bot_context(guild):
    m = Mock(spec=commands.Context)
    m.guild = guild
    m.bot = mock_karma_bot()
    return m
