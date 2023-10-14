import pytest
from bot.memory_store import KarmaMemoryStore

@pytest.fixture
def karma_store():
    return KarmaMemoryStore()

@pytest.mark.asyncio
async def test_open_and_close(karma_store):
    await karma_store.open()
    assert hasattr(karma_store, 'karma_map')
    assert karma_store.karma_map == {}
    await karma_store.close()
    assert not hasattr(karma_store, 'karma_map')

@pytest.mark.asyncio
async def test_create_if_doesnt_exist(karma_store):
    guild_id = 123
    user_id = 456

    await karma_store.open()
    karma_store.create_if_doesnt_exist(guild_id, user_id)
    assert guild_id in karma_store.karma_map
    assert user_id in karma_store.karma_map[guild_id]
    assert karma_store.karma_map[guild_id][user_id] == 0

@pytest.mark.asyncio
async def test_upvote_user(karma_store):
    guild_id = 123
    user_id = 456

    await karma_store.open()
    karma = await karma_store.upvote_user(guild_id, user_id)
    assert karma == 1
    assert karma_store.karma_map[guild_id][user_id] == 1

@pytest.mark.asyncio
async def test_downvote_user(karma_store):
    guild_id = 123
    user_id = 456

    await karma_store.open()
    karma = await karma_store.downvote_user(guild_id, user_id)
    assert karma == -1
    assert karma_store.karma_map[guild_id][user_id] == -1

@pytest.mark.asyncio
async def test_get_karma_of_user(karma_store):
    guild_id = 123
    user_id = 456

    await karma_store.open()
    karma = await karma_store.get_karma_of_user(guild_id, user_id)
    assert karma == 0

@pytest.mark.asyncio
async def test_get_top_users(karma_store):
    guild_id = 123

    await karma_store.open()

    await karma_store.upvote_user(guild_id, 1)
    await karma_store.upvote_user(guild_id, 2)
    await karma_store.upvote_user(guild_id, 3)

    top_users = await karma_store.get_top_users(guild_id, 2)
    assert top_users == [(1, 1), (2, 1)]

@pytest.mark.asyncio
async def test_set_guild_karma(karma_store):
    guild_id = 123
    karma = {1: 10, 2: 20}

    await karma_store.open()
    await karma_store.set_guild_karma(guild_id, karma)
    assert karma_store.karma_map[guild_id] == karma

def test_str_method(karma_store):
    assert str(karma_store) == 'KarmaMemoryStore'
