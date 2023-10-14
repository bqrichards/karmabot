import pytest
import tempfile
import os
from bot.sqlite_store import KarmaSqliteStore

@pytest.fixture
def sqlite_store():
    # Create a temporary SQLite database for testing
    _, temp_filepath = tempfile.mkstemp()
    store = KarmaSqliteStore(temp_filepath)
    yield store
    # Clean up the temporary database file
    os.remove(temp_filepath)

@pytest.mark.asyncio
async def test_open_and_close(sqlite_store):
    await sqlite_store.open()
    assert hasattr(sqlite_store, 'connection')
    assert sqlite_store.connection is not None
    await sqlite_store.close()

@pytest.mark.asyncio
async def test_create_if_doesnt_exist(sqlite_store):
    guild_id = 123
    user_id = 456

    await sqlite_store.open()
    sqlite_store.create_if_doesnt_exist(guild_id, user_id)

    cur = sqlite_store.connection.cursor()
    cur.execute('SELECT karma FROM karma WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    result = cur.fetchone()
    cur.close()

    await sqlite_store.close()

    assert result is not None
    assert result[0] == 0

@pytest.mark.asyncio
async def test_upvote_user(sqlite_store):
    guild_id = 123
    user_id = 456

    await sqlite_store.open()
    karma = await sqlite_store.upvote_user(guild_id, user_id)
    await sqlite_store.close()

    assert karma == 1

@pytest.mark.asyncio
async def test_downvote_user(sqlite_store):
    guild_id = 123
    user_id = 456

    await sqlite_store.open()
    karma = await sqlite_store.downvote_user(guild_id, user_id)
    await sqlite_store.close()

    assert karma == -1

@pytest.mark.asyncio
async def test_get_karma_of_user(sqlite_store):
    guild_id = 123
    user_id = 456

    await sqlite_store.open()
    karma = await sqlite_store.get_karma_of_user(guild_id, user_id)
    await sqlite_store.close()

    assert karma == 0

@pytest.mark.asyncio
async def test_get_top_users(sqlite_store):
    guild_id = 123

    await sqlite_store.open()
    for i in range(1, 6):
        for _ in range(i):
            await sqlite_store.upvote_user(guild_id, i)

    top_users = await sqlite_store.get_top_users(guild_id, 3)

    await sqlite_store.close()

    assert top_users == [(5, 5), (4, 4), (3, 3)]

@pytest.mark.asyncio
async def test_set_guild_karma(sqlite_store):
    guild_id = 123
    karma = {1: 10, 2: 20}

    await sqlite_store.open()
    await sqlite_store.set_guild_karma(guild_id, karma)

    cur = sqlite_store.connection.cursor()
    cur.execute('SELECT user_id, karma FROM karma WHERE guild_id = ?', (guild_id,))
    result = cur.fetchall()
    cur.close()
    await sqlite_store.close()

    assert len(result) == 2
    assert (1, 10) in result
    assert (2, 20) in result

def test_str_method(sqlite_store):
    assert str(sqlite_store) == 'KarmaSqliteStore'
