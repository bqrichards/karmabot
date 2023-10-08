from discord import TextChannel
from bot.config import KarmaConfig
from bot.memory_store import KarmaMemoryStore


class MockKarmaBot():
    def __init__(self) -> None:
        self.store = KarmaMemoryStore()
        self.config = KarmaConfig(upvote_emojis=['👍'], downvote_emojis=['👎'], command_prefix='?')

class MockKarmaBotContext:
    def __init__(self, guild):
        self.guild = guild
        self.bot = MockKarmaBot()

class MockGuild:
    def __init__(self, id: int):
        self.id = id
        self.channels = []

class MockAuthor:
    def __init__(self, id: int) -> None:
        self.id = id

class MockReaction:
    def __init__(self, upvote=False) -> None:
        if upvote:
            self.emoji = '👍'
        else:
            self.emoji = '👎'
    
    def __repr__(self) -> str:
        return f'MockReaction_emoji={self.emoji}'

class MockMessage:
    def __init__(self, upvotes=0, downvotes=0) -> None:
        self.author = MockAuthor(456)
        self.reactions = [MockReaction(upvote=True) for _ in range(upvotes)]
        self.reactions.extend(MockReaction(upvote=False) for _ in range(downvotes))
        print(self.reactions)

class MockTextChannelHistory:
    def __init__(self, limit = 1000) -> None:
        self.messages = [MockMessage(upvotes=2), MockMessage(downvotes=1)]

    def __aiter__(self):
        self.iter_keys = iter(self.messages)
        return self

    async def __anext__(self):
        try:
            k = next(self.iter_keys)
        except StopIteration:
            raise StopAsyncIteration
        
        return k

class MockTextChannel(TextChannel):
    def __init__(self) -> None:
        ...

    def history(self, limit=10):
        return MockTextChannelHistory(limit=limit)