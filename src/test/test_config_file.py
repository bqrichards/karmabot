import pytest
import json
from unittest.mock import MagicMock, patch, mock_open
from bot.config_file import ConfigJsonReader

test_config_json = """{
    "upvote_emojis": ["🚀"],
    "downvote_emojis": ["👹"],
    "command_prefix": "<"
}"""

invalid_config_json = """{
    "upvote_emojis": ["🚀"],
    "downvote_emojis": ["👹"],
    "command_prefix": "<"
"""

@patch('builtins.open', mock_open(read_data=test_config_json))
def test_loaded_upvote_emojis():
    config = ConfigJsonReader('fake_path').get_config()
    assert len(config.upvote_emojis) == 1
    assert config.upvote_emojis[0] == '🚀'

@patch('builtins.open', mock_open(read_data=test_config_json))
def test_loaded_downvote_emojis():
    config = ConfigJsonReader('fake_path').get_config()
    assert len(config.downvote_emojis) == 1
    assert config.downvote_emojis[0] == '👹'

@patch('builtins.open', mock_open(read_data=test_config_json))
def test_loaded_command_prefix():
    config = ConfigJsonReader('fake_path').get_config()
    assert config.command_prefix == '<'

def test_file_doesnt_exist():
    with patch('builtins.open', mock_open()) as mocked_open:
        mocked_open.side_effect = IOError()
        with pytest.raises(IOError):
            ConfigJsonReader('fake_path').get_config()

@patch('builtins.open', mock_open(read_data=invalid_config_json))
def test_invalid_json():
    with pytest.raises(json.decoder.JSONDecodeError):
        ConfigJsonReader('fake_path').get_config()
