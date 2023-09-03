import logging
from bot.store import KarmaStore


class KarmaMemoryStore(KarmaStore):
    """An in-memory store for karma"""

    karma_map: dict[int, dict[int, int]]
    """karma_map[guild_id][user_id] -> karma amount"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__class__.__name__)
    
    async def open(self):
        self.karma_map = dict()
        self.logger.info('Store opened')
    
    async def close(self):
        del self.karma_map
        self.logger.info('Store closed')

    def create_if_doesnt_exist(self, guild_id: int, user_id: int):
        """Initialize a user's karma in a guild to 0 (if it doesn't already exist)"""
        if not guild_id in self.karma_map:
            self.karma_map[guild_id] = dict()

        if not user_id in self.karma_map[guild_id]:
            self.karma_map[guild_id][user_id] = 0

    async def upvote_user(self, guild_id: int, user_id: int) -> int:
        self.create_if_doesnt_exist(guild_id, user_id)

        self.karma_map[guild_id][user_id] += 1
        self.logger.debug(self.karma_map)

        return self.karma_map[guild_id][user_id]

    async def downvote_user(self, guild_id: int, user_id: int) -> int:
        self.create_if_doesnt_exist(guild_id, user_id)

        self.karma_map[guild_id][user_id] -= 1
        self.logger.debug(self.karma_map)

        return self.karma_map[guild_id][user_id]

    async def get_karma_of_user(self, guild_id: int, user_id: int) -> int:
        guild_map = self.karma_map.get(guild_id, dict())
        karma_amount = guild_map.get(user_id, 0)

        return karma_amount
    
    async def get_top_users(self, guild_id: int, number_of_users: int) -> list[tuple[int, int]]:
        top_users = self.karma_map.get(guild_id, dict())
        top_users = sorted(top_users.items(), key=lambda item: item[1])
        top_users = top_users[:number_of_users]

        return top_users

    async def set_guild_karma(self, guild_id: int, karma: dict[int, int]) -> None:
        self.karma_map[guild_id] = karma

    def __str__(self) -> str:
        return 'KarmaMemoryStore'
