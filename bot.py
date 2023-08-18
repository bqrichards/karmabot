import os
import discord
from typing import Optional
from dotenv import load_dotenv


load_dotenv()


TOKEN = os.getenv('KARMABOT_TOKEN')
if not TOKEN:
	raise ValueError('KARMABOT_TOKEN env variable missing')


class KarmaClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		upvote_list = ['⬆️', '☝️', '👍']
		downvote_list = [ '⬇️', '👇', '👎']

		self.upvote_emojis = [discord.PartialEmoji(name=emoji) for emoji in upvote_list]
		self.downvote_emojis = [discord.PartialEmoji(name=emoji) for emoji in downvote_list]


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

client = KarmaClient(intents=intents)
client.run(TOKEN)
