import os
import logging
import discord
from typing import Optional
from discord.ext import commands

from bot.config import KarmaConfig
from bot.store import KarmaStore


class KarmaBot(commands.Bot):
	"""Discord bot for monitoring karma.
	
	Permissions needed:
	- Read Messages/View Channels
	- Send Messages
	- Read Message History
	- Use External Emojis
	- Use External Stickers
	"""

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

		@self.event
		async def on_ready():
			self.logger.info(f'Logged in as {self.user}')

	async def setup_hook(self) -> None:
		self.logger.info('Opening karma store')
		await self.store.open()
		self.logger.info('Loading cogs')
		for filename in os.listdir('./src/bot/cogs'):
			if filename.endswith('.py'):
				await self.load_extension(f'bot.cogs.{filename[:-3]}')
		await super().setup_hook()

	async def get_message_sender_id(self, payload: discord.RawReactionActionEvent) -> Optional[int]:
		"""Get the sender of a message that was the subject of a RawReactionActionEvent"""
		if payload.guild_id is None:
			return None

		guild = self.get_guild(payload.guild_id)
		if guild is None:
			# Check if we're still in the guild and it's cached.
			return None
		
		channel = guild.get_channel(payload.channel_id)
		if channel is None or not isinstance(channel, discord.TextChannel):
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


KarmaBotContext = commands.Context[KarmaBot]
"""Type for the commands.Context with `KarmaBot` as the bot"""
