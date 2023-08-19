# karmabot

## Summary

This Discord bot will be used to track "karma" of users, similar to Reddit. Upvote and downvote reactions will be counted and be able to be queried for.

## How to run

First, install dependencies with Poetry.

`poetry install`

Then, run the main bot script with Poetry.

`poetry run python src/bot.py`

## Commands

| key                     | description                                                            |
|-------------------------|------------------------------------------------------------------------|
| `?karma [user]`         | Replies with the karma of the user. If no user specified, uses sender. |

## Config

Edit the configuration file located at `config.json`.

### All config options

| key                      | description                                                       | type   | default |
|--------------------------|-------------------------------------------------------------------|--------|---------|
| upvote_reaction          | A list of emoji OR name of server emotes that represent upvotes   | list[string] | ["⬆️", "👆", "👍"]      |
| downvote_reaction        | A list of emoji OR name of server emotes that represent downvotes | list[string] | ["⬇️", "👇", "👎"]      | 
| command_prefix           | The command prefix for KarmaBot                                   | string | ?       | 

## License

See [LICENSE](https://github.com/bqrichards/karmabot/blob/main/LICENSE)
