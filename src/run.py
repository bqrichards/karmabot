import os
import logging
import discord
import sys

from bot.bot import KarmaBot
from bot.config import ConfigProvider
from bot.config_file import ConfigJsonReader
from bot.store import KarmaStore
# from bot.memory_store import KarmaMemoryStore
from bot.sqlite_store import KarmaSqliteStore

from dotenv import load_dotenv
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

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True # needed for get_member_named
    intents.message_content = True # needed for on_message

    logger = logging.getLogger(__name__)

    config_provider: ConfigProvider = ConfigJsonReader(filepath='config.json')
    try:
        config = config_provider.get_config()
    except Exception as e:
        logger.error(f'Exiting with error loading config: {e}')
        sys.exit(1)

    # store: KarmaStore = KarmaMemoryStore()
    store: KarmaStore = KarmaSqliteStore(filepath='data/karma.db')
    
    bot = KarmaBot(intents=intents, config=config, store=store)

    bot.run(TOKEN)
