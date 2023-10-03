from bot.config import config_from_dict


def test_default_upvote_emojis():
    output = config_from_dict({})
    assert output.upvote_emojis == ['⬆️', '👆', '👍']

def test_default_downvote_emojis():
    output = config_from_dict({})
    assert output.downvote_emojis == ['⬇️', '👇', '👎']

def test_default_command_prefix():
    output = config_from_dict({})
    assert output.command_prefix == '?'