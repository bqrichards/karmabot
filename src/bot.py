import logging
import os
from typing import Optional
import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import ConfigProvider, KarmaConfig
from config_file import ConfigJsonReader
# from memory_store import KarmaMemoryStore
from karma_command import karma_command
from sqlite_store import KarmaSqliteStore
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


class KarmaBot(commands.Bot):
	config: KarmaConfig
	store: KarmaStore

	upvote_emojis: list[discord.PartialEmoji]
	downvote_emojis: list[discord.PartialEmoji]

	def __init__(self, config: KarmaConfig, store: KarmaStore, *args, **kwargs):
		super().__init__(command_prefix=config.command_prefix, *args, **kwargs)
		self.config = config
		self.store = store

		self.upvote_emojis = [discord.PartialEmoji(name=emoji) for emoji in config.upvote_emojis]
		self.downvote_emojis = [discord.PartialEmoji(name=emoji) for emoji in config.downvote_emojis]

		self.logger = logging.getLogger(__class__.__name__)
		self.logger.info('Creating bot with config: ' + str(self.config) + ", store: " + str(self.store) + ', logger: ' + str(self.logger))

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
		"""Whether this emoji is an upvote"""
		return emoji in self.upvote_emojis

	def reaction_is_downvote(self, emoji: discord.PartialEmoji) -> bool:
		"""Whether this emoji is an downvote"""
		return emoji in self.downvote_emojis
	
	async def close(self) -> None:
		self.logger.info('Closing karma store')
		await self.store.close()
		self.logger.info('Logging out')
		await super().close()


intents = discord.Intents.default()
intents.members = True # needed for get_member_named
intents.message_content = True # needed for on_message

config_provider: ConfigProvider = ConfigJsonReader(filepath='config.json')
config = config_provider.get_config()

store: KarmaStore = KarmaSqliteStore(filepath='data/karma.db')

bot = KarmaBot(intents=intents, config=config, store=store)

@bot.event
async def on_ready():
	bot.logger.info('Opening karma store')
	await bot.store.open()
	bot.logger.info(f'Logged in as {bot.user}')
	bot.logger.info('------')

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
	if not payload.guild_id or not payload.user_id:
		bot.logger.error('guild_id or user_id not defined')
		return

	try:
		sender_id = await bot.get_message_sender_id(payload)
	except Exception as e:
		bot.logger.error('Error getting message sender: ' + str(e))
		return

	bot.logger.debug(f'Add reaction, message sender id: {sender_id}')
	if bot.reaction_is_upvote(payload.emoji):
		await bot.store.upvote_user(payload.guild_id, payload.user_id)
	elif bot.reaction_is_downvote(payload.emoji):
		await bot.store.downvote_user(payload.guild_id, payload.user_id)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
	if not payload.guild_id or not payload.user_id:
		bot.logger.error('guild_id or user_id not defined')
		return

	try:
		sender_id = await bot.get_message_sender_id(payload)
	except Exception as e:
		bot.logger.error('Error getting message sender: ' + str(e))
		return

	bot.logger.debug(f'Remove reaction, message sender id: {sender_id}')
	if bot.reaction_is_upvote(payload.emoji):
		await bot.store.downvote_user(payload.guild_id, payload.user_id)
	elif bot.reaction_is_downvote(payload.emoji):
		await bot.store.upvote_user(payload.guild_id, payload.user_id)

@bot.command()
async def karma(ctx: commands.Context, member_name: Optional[str]=None):
	await karma_command(ctx, bot.store, member_name)


if __name__ == '__main__':
	bot.run(TOKEN)
