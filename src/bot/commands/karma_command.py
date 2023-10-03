import logging
import re
from typing import Optional

from bot.bot import KarmaBotContext


async def karma_command(ctx: KarmaBotContext, target_member: Optional[str]=None) -> None:
    logger = logging.getLogger(__name__)

    # Get user id
    if not ctx.guild:
        logger.debug('Guild could not be found on message')
        return
    
    guild_id = ctx.guild.id

    if target_member:
        # Lookup user in guild
        # Check if <@user_id> format
        mention_format = r'^<@(\d+)>$'
        mention_matches = re.match(mention_format, target_member)
        if mention_matches:
            target_user_id = int(mention_matches.group(1))
        else:
            target_user_member = ctx.guild.get_member_named(target_member)
            if target_user_member is None:
                await ctx.reply('Could not find a member with that name')
                logger.debug(f'Member {target_member} could not be found in guild')
                return
            target_user_id = target_user_member.id
    else:
        target_user_id = ctx.message.author.id

    logger.debug(f'Fetching karma for user {target_user_id}')
    
    karma = await ctx.bot.store.get_karma_of_user(guild_id, target_user_id)
    logger.debug(f'Fetched karma: {karma}')

    await ctx.reply(f'{karma}')
