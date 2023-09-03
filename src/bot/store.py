class KarmaStore:
    """A store for karma"""

    async def open(self) -> None:
        """Open the store"""
        ...

    async def close(self) -> None:
        """Close the store"""
        ...

    async def upvote_user(self, guild_id: int, user_id: int) -> int:
        """Upvote a user in a guild. Returns the karma after the upvote."""
        ...
    
    async def downvote_user(self, guild_id: int, user_id: int) -> int:
        """Downvote a user in a guild. Returns the karma after the downvote."""
        ...
    
    async def get_karma_of_user(self, guild_id: int, user_id: int) -> int:
        """Get the karma of a user in a guild"""
        ...

    async def get_top_users(self, guild_id: int, number_of_users: int) -> list[tuple[int, int]]:
        """Get the leaderboard of a guild"""
        ...
    
    async def set_guild_karma(self, guild_id: int, karma: dict[int, int]) -> None:
        """Set a guild's users and karma values"""
        ...
