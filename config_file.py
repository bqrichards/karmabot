import json
from config import ConfigProvider, KarmaConfig, config_from_dict


class ConfigJsonReader(ConfigProvider):
    """Config Provider that reads JSON file"""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_config(self) -> KarmaConfig:
        with open(self.filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return config_from_dict(data)
