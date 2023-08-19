from config import ConfigProvider, KarmaConfig, config_from_dict
import json


class ConfigJsonReader(ConfigProvider):
    def __init__(self, filepath: str):
        self.filepath = filepath
    
    def get_config(self) -> KarmaConfig:
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        
        return config_from_dict(data)
