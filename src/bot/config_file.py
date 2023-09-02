import json
import logging
from bot.config import ConfigProvider, KarmaConfig, config_from_dict


class ConfigJsonReader(ConfigProvider):
    """Config Provider that reads JSON file"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.logger = logging.getLogger(__class__.__name__)

    def get_config(self) -> KarmaConfig:
        with open(self.filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        self.logger.info(f'Loaded config from {self.filepath}: {data}')
        
        return config_from_dict(data)
