import logging
import discord
from discord.ext import commands

from store import KarmaStore

def get_display_name(member: discord.Member | None) -> str:
    if member is None:
        return '(unknown)'

    return member.display_name


async def leaderboard_command(ctx: commands.Context, store: KarmaStore, member_count: int):
    logger = logging.getLogger('leaderboard_command')
    guild = ctx.guild
    if guild is None:
        logger.error('Guild is None')
        return
    
    top_users = await store.get_top_users(guild.id, member_count)

    def get_user_name(user_id: int):
        return get_display_name(guild.get_member(user_id))

    # Format message
    message_header = f'Leaderboard for {guild.name}'
    message_seperator = '-' * len(message_header)
    message_user_counts = '\n'.join(f'{get_user_name(user_id)} - {karma}' for user_id, karma in top_users)
    if len(message_user_counts) == 0:
        message_user_counts = '*crickets*'

    message = f"""{message_header}
{message_seperator}
{message_user_counts}"""

    await ctx.reply(message)
