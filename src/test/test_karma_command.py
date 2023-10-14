from unittest.mock import Mock
import discord
import pytest
from bot.commands.karma_command import karma_command
from test.mocks import mock_guild, mock_karma_bot_context, mock_karma_store

@pytest.mark.asyncio
async def test_guild_none():
    ctx = mock_karma_bot_context(None)
    
    await karma_command(ctx, None)

    # Returned early
    assert not ctx.reply.called

@pytest.mark.asyncio
async def test_no_target_member():
    guild_id = 4123123
    sender_id = 16222
    karma_value = 101

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    ctx.bot.store = mock_karma_store()
    ctx.message.author.id = sender_id
    ctx.bot.store.get_karma_of_user.return_value = karma_value
    
    await karma_command(ctx, None)

    ctx.bot.store.get_karma_of_user.assert_called_with(guild_id, sender_id)
    ctx.reply.assert_called_with(f'{karma_value}')

@pytest.mark.asyncio
async def test_mention_target_member():
    """Test when message is @username (mention) format"""
    guild_id = 4123123
    target_id = 878718272
    karma_value = 101

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    ctx.message.author.id = target_id
    ctx.bot.store.get_karma_of_user.return_value = karma_value
    
    await karma_command(ctx, f'<@{target_id}>')

    ctx.bot.store.get_karma_of_user.assert_called_with(guild_id, target_id)
    ctx.reply.assert_called_with(f'{karma_value}')

@pytest.mark.asyncio
async def test_target_member_not_found():
    """Test reply with member cannot be found"""
    guild_id = 4123123

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    ctx.guild.get_member_named.return_value = None
    
    await karma_command(ctx, 'nonExistantUsername')

    ctx.reply.assert_called_with('Could not find a member with that name')

@pytest.mark.asyncio
async def test_target_member_found():
    """Test reply with member can be found"""
    guild_id = 4123123
    member_id = 31233
    karma_value = 1222

    ctx = mock_karma_bot_context(mock_guild(guild_id))
    ctx.guild.get_member_named.return_value = Mock(spec=discord.Member)
    ctx.guild.get_member_named.return_value.id = member_id
    ctx.bot.store.get_karma_of_user.return_value = karma_value

    await karma_command(ctx, 'existingUsername')

    ctx.bot.store.get_karma_of_user.assert_called_with(guild_id, member_id)
    ctx.reply.assert_called_with(f'{karma_value}')
