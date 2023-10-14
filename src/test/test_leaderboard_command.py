from unittest.mock import AsyncMock, Mock, patch
import pytest

import discord

from bot.commands.leaderboard_command import get_display_name, leaderboard_command
from test.mocks import mock_guild, mock_karma_bot_context


def test_get_display_name_none():
    assert get_display_name(None) == '(unknown)'

def test_get_display_name():
    member_mock = Mock(spec=discord.Member)
    member_mock.display_name = 'TestUser123'

    assert get_display_name(member_mock) == 'TestUser123'

@pytest.mark.asyncio
async def test_guild_none():
    ctx = mock_karma_bot_context(None)

    ctx.bot.store.get_top_users = AsyncMock()
    
    await leaderboard_command(ctx, 0)

    # Fix Assert returned early
    assert not ctx.bot.store.get_top_users.called

@pytest.mark.asyncio
async def test_leaderboard_no_members():
    guild_id = 5

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    await ctx.bot.store.open()
    ctx.bot.store.get_top_users = AsyncMock(return_value=[])

    await leaderboard_command(ctx, 0)

    ctx.reply.assert_called_with('Leaderboard for Mock Guild\n--------------------------\n*crickets*')

@pytest.mark.asyncio
@patch('bot.commands.leaderboard_command.get_display_name')
async def test_leaderboard_members(mocked_get_display_name):
    guild_id = 5

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    await ctx.bot.store.open()
    ctx.bot.store.get_top_users = AsyncMock(return_value=[
        (105, 4),
        (101, 99),
    ])

    mocked_get_display_name.side_effect = ['Member 105', 'Member 101']

    await leaderboard_command(ctx, 0)

    ctx.reply.assert_called_with('Leaderboard for Mock Guild\n--------------------------\nMember 105 - 4\nMember 101 - 99')

@pytest.mark.asyncio
async def test_leaderboard_member_none():
    guild_id = 5

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    await ctx.bot.store.open()
    ctx.bot.store.get_top_users = AsyncMock(return_value=[
        (105, 7),
        (101, 9),
    ])

    ctx.guild.get_member.return_value = None

    await leaderboard_command(ctx, 0)

    ctx.reply.assert_called_with('Leaderboard for Mock Guild\n--------------------------\n(unknown) - 7\n(unknown) - 9')
