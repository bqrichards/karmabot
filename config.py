from dataclasses import dataclass


@dataclass
class KarmaConfig:
    """Config for KarmaBot"""

    upvote_emojis: list[str]
    """List of emojis that are considered upvotes"""

    downvote_emojis: list[str]
    """List of emojis that are considered downvotes"""


class ConfigProvider:
    """Interface for provider of KarmaConfig"""

    def get_config(self) -> KarmaConfig:
        """Get config"""


def config_from_dict(obj: dict) -> KarmaConfig:
    """Returns a config object from a generic dict. Any missing keys will use default values"""
    upvote_emojis = obj.get('upvote_emojis', ['⬆️', '👆', '👍'])
    downvote_emojis = obj.get('downvote_emojis', ['⬇️', '👇', '👎'])

    return KarmaConfig(upvote_emojis, downvote_emojis)
