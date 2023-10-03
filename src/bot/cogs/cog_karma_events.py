import discord
from discord.ext import commands

from bot.bot import KarmaBot


class KarmaBotReactionCog(commands.Cog):
    def __init__(self, bot: KarmaBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            self.bot.logger.error('guild_id not defined')
            return

        try:
            sender_id = await self.bot.get_message_sender_id(payload)
        except Exception as e:
            self.bot.logger.error('Error getting message sender: ' + str(e))
            return
    
        if sender_id is None:
            self.bot.logger.error('sender_id is None')
            return

        self.bot.logger.debug(f'Add reaction, message sender: {sender_id}')
        if self.bot.reaction_is_upvote(payload.emoji):
            await self.bot.store.upvote_user(payload.guild_id, sender_id)
        elif self.bot.reaction_is_downvote(payload.emoji):
            await self.bot.store.downvote_user(payload.guild_id, sender_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            self.bot.logger.error('guild_id or user_id not defined')
            return

        try:
            sender_id = await self.bot.get_message_sender_id(payload)
        except Exception as e:
            self.bot.logger.error('Error getting message sender: ' + str(e))
            return
        
        if sender_id is None:
            self.bot.logger.error('sender_id is None')
            return

        self.bot.logger.debug(f'Remove reaction, message sender id: {sender_id}')
        if self.bot.reaction_is_upvote(payload.emoji):
            await self.bot.store.downvote_user(payload.guild_id, sender_id)
        elif self.bot.reaction_is_downvote(payload.emoji):
            await self.bot.store.upvote_user(payload.guild_id, sender_id)


async def setup(bot: KarmaBot):
    await bot.add_cog(KarmaBotReactionCog(bot))
