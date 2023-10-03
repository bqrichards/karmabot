import pathlib
from bot.config_file import ConfigJsonReader


def get_config():
    filepath = str((pathlib.Path(__file__).parent / 'resources' / 'config-test01.json').resolve())
    config_reader = ConfigJsonReader(filepath)
    config = config_reader.get_config()
    return config


def test_loaded_upvote_emojis():
    config = get_config()
    assert len(config.upvote_emojis) == 1
    assert config.upvote_emojis[0] == '🚀'


def test_loaded_downvote_emojis():
    config = get_config()
    assert len(config.downvote_emojis) == 1
    assert config.downvote_emojis[0] == '👹'


def test_loaded_command_prefix():
    config = get_config()
    assert config.command_prefix == '<'
