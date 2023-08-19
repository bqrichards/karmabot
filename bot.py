import logging
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


def setup_logger():
	log_level = os.environ.get('LOG_LEVEL', 'INFO')
	logging.basicConfig()
	logging.getLogger().setLevel(log_level)
	print(f'Setting log level to {log_level}')


setup_logger()


class KarmaClient(discord.Client):
	config: KarmaConfig
	store: KarmaStore

	upvote_emojis: list[discord.PartialEmoji]
	downvote_emojis: list[discord.PartialEmoji]

	def __init__(self, config: KarmaConfig, store: KarmaStore, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = config
		self.store = store
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.info('Creating bot with config: ' + str(self.config) + ", store: " + str(self.store) + ', logger: ' + str(self.logger))

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


	def reaction_is_upvote(self, emoji: discord.PartialEmoji) -> bool:
		return emoji in self.upvote_emojis


	def reaction_is_downvote(self, emoji: discord.PartialEmoji) -> bool:
		return emoji in self.downvote_emojis


	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if not payload.guild_id or not payload.user_id:
			self.logger.error('guild_id or user_id not defined')
			return

		try:
			sender_id = await self.get_message_sender_id(payload)
		except Exception as e:
			self.logger.error('Error getting message sender: ' + str(e))
			return

		self.logger.debug(f'Add reaction, message sender id: {sender_id}')
		if self.reaction_is_upvote(payload.emoji):
			self.store.upvote_user(payload.guild_id, payload.user_id)
		elif self.reaction_is_downvote(payload.emoji):
			self.store.downvote_user(payload.guild_id, payload.user_id)


	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		if not payload.guild_id or not payload.user_id:
			self.logger.error('guild_id or user_id not defined')
			return

		try:
			sender_id = await self.get_message_sender_id(payload)
		except Exception as e:
			self.logger.error('Error getting message sender: ' + str(e))
			return

		self.logger.debug(f'Remove reaction, message sender id: {sender_id}')
		if self.reaction_is_upvote(payload.emoji):
			self.store.downvote_user(payload.guild_id, payload.user_id)
		elif self.reaction_is_downvote(payload.emoji):
			self.store.upvote_user(payload.guild_id, payload.user_id)


intents = discord.Intents.default()

config_provider: ConfigProvider = ConfigJsonReader(filepath='config.json')
config = config_provider.get_config()

store: KarmaStore = KarmaMemoryStore()

client = KarmaClient(intents=intents, config=config, store=store)
client.run(TOKEN)
