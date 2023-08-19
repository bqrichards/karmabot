class KarmaStore:
    """A store for karma"""

    def upvote_user(self, guild_id: int, user_id: int) -> int:
        """Upvote a user in a guild. Returns the karma after the upvote."""
        pass
    
    def downvote_user(self, guild_id: int, user_id: int) -> int:
        """Downvote a user in a guild. Returns the karma after the downvote."""
        pass
    
    def get_karma_of_user(self, guild_id: int, user_id: int) -> int:
        """Get the karma of a user in a guild"""
        pass
