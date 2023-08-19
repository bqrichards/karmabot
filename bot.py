import os
import discord
from typing import Optional
from dotenv import load_dotenv

from config import ConfigProvider, KarmaConfig
from config_file import ConfigJsonReader
from memory_store import KarmaMemoryStore
from store import KarmaStore


load_dotenv()


TOKEN = os.getenv('KARMABOT_TOKEN')
if not TOKEN:
	raise ValueError('KARMABOT_TOKEN env variable missing')


class KarmaClient(discord.Client):
	config: KarmaConfig
	store: KarmaStore

	upvote_emojis: list[discord.PartialEmoji]
	downvote_emojis: list[discord.PartialEmoji]

	def __init__(self, config: KarmaConfig, store: KarmaStore, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = config
		self.store = store
		print('Creating bot with config: ' + str(self.config) + ", store: " + str(self.store))

		self.upvote_emojis = [discord.PartialEmoji(name=emoji) for emoji in config.upvote_emojis]
		self.downvote_emojis = [discord.PartialEmoji(name=emoji) for emoji in config.downvote_emojis]


	async def get_message_sender_id(self, payload: discord.RawReactionActionEvent) -> Optional[int]:
		"""Get the sender of a message that was the subject of a RawReactionActionEvent"""
		if payload.guild_id is None:
			return None

		guild = self.get_guild(payload.guild_id)
		if guild is None:
			# Check if we're still in the guild and it's cached.
			return None
		
		channel = guild.get_channel(payload.channel_id)
		if channel is None or type(channel) != discord.channel.TextChannel:
			return None

		message = await channel.get_partial_message(payload.message_id).fetch()
		sender_id = message.author.id

		return sender_id


	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		try:
			sender_id = await self.get_message_sender_id(payload)
		except Exception as e:
			print('Error getting message sender: ' + str(e))
			return

		print(f'Add reaction, message sender id: {sender_id}')


	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		try:
			sender_id = await self.get_message_sender_id(payload)
		except Exception as e:
			print('Error getting message sender: ' + str(e))
			return

		print(f'Remove reaction, message sender id: {sender_id}')


intents = discord.Intents.default()

config_provider: ConfigProvider = ConfigJsonReader(filepath='config.json')
config = config_provider.get_config()

store: KarmaStore = KarmaMemoryStore()

client = KarmaClient(intents=intents, config=config, store=store)
client.run(TOKEN)
