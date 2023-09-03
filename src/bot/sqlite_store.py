import logging
from bot.store import KarmaStore


class KarmaSqliteStore(KarmaStore):
    """An SQLite store for karma"""

    def __init__(self, filepath: str) -> None:
        self.logger = logging.getLogger(__class__.__name__)
        self.filepath = filepath

        # Only import sqlite3 if class is instantiated
        import sqlite3
        self.sqlite3 = sqlite3
    
    async def open(self):
        self.connection = self.sqlite3.connect(self.filepath)
        self.logger.info(f'Store opened at {self.filepath}')
        self.initialize_database()

    async def close(self):
        self.connection.close()
        self.logger.info('Store closed')

    def initialize_database(self):
        cur = self.connection.cursor()
        self.logger.debug('initialize_database')
        cur.execute('CREATE TABLE IF NOT EXISTS karma(guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL, karma INTEGER NOT NULL, PRIMARY KEY (guild_id, user_id));')
        cur.close()
    
    def create_if_doesnt_exist(self, guild_id: int, user_id: int):
        cur = self.connection.cursor()
        cur.execute('INSERT OR IGNORE INTO karma (guild_id, user_id, karma) VALUES (?, ?, ?)', (guild_id, user_id, 0,))
        self.connection.commit()
        cur.close()

    async def upvote_user(self, guild_id: int, user_id: int) -> int:
        self.create_if_doesnt_exist(guild_id, user_id)

        cur = self.connection.cursor()
        cur.execute('UPDATE karma SET karma = karma + 1 WHERE (guild_id, user_id) = (?, ?)', (guild_id, user_id,))
        self.connection.commit()
        cur.close()

        return await self.get_karma_of_user(guild_id, user_id)

    async def downvote_user(self, guild_id: int, user_id: int) -> int:
        self.create_if_doesnt_exist(guild_id, user_id)

        cur = self.connection.cursor()
        cur.execute('UPDATE karma SET karma = karma - 1 WHERE (guild_id, user_id) = (?, ?)', (guild_id, user_id,))
        self.connection.commit()
        cur.close()

        return await self.get_karma_of_user(guild_id, user_id)

    async def get_karma_of_user(self, guild_id: int, user_id: int) -> int:
        pk = (guild_id, user_id,)
        cur = self.connection.cursor()
        cur.execute('SELECT karma FROM karma WHERE guild_id = ? AND user_id = ?', pk)
        existing_karma = cur.fetchone()
        cur.close()

        if existing_karma is None:
            existing_karma = 0
        else:
            existing_karma = existing_karma[0]

        return existing_karma
    
    async def get_top_users(self, guild_id: int, number_of_users: int) -> list[tuple[int, int]]:
        cur = self.connection.cursor()
        cur.execute('SELECT user_id, karma FROM karma WHERE guild_id = ? ORDER BY karma DESC LIMIT ?', (guild_id, number_of_users))
        top_users = cur.fetchall()
        cur.close()

        return top_users

    async def set_guild_karma(self, guild_id: int, karma: dict[int, int]) -> None:
        cur = self.connection.cursor()
        for user_id, karma_amount in karma.items():
            cur.execute('INSERT INTO karma (guild_id, user_id, karma) VALUES (?, ?, ?) ON CONFLICT (guild_id, user_id) DO UPDATE SET guild_id=excluded.guild_id, user_id=excluded.user_id, karma=excluded.karma', (guild_id, user_id, karma_amount,))
        self.connection.commit()
        cur.close()

    def __str__(self) -> str:
        return __class__.__name__
