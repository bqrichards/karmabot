# karmabot <!-- omit in toc -->

## Outline <!-- omit in toc -->

- [Summary](#summary)
- [How to run](#how-to-run)
- [Commands](#commands)
- [Config](#config)
- [Environment](#environment)
- [Roadmap](#roadmap)
- [License](#license)

## Summary

This Discord bot will be used to track "karma" of users, similar to Reddit. Upvote and downvote reactions will be counted and be able to be queried for.

## How to run

First, install dependencies with Poetry.

`poetry install`

Then, set the `KARMABOT_TOKEN` environment variable. See the [Environment](#environment) section for more info. `.env` should look like this:

```
KARMABOT_TOKEN=...
```

Finally, run the main bot script with Poetry.

`poetry run python src/bot.py`

## Commands

| key                           | description                                                            |
| ----------------------------- | ---------------------------------------------------------------------- |
| `?karma [user]`               | Replies with the karma of the user. If no user specified, uses sender. |
| `?leaderboard [member_count]` | Replies with the users that have the most karma in the guild.          |
| `?scan`                       | Scan the guild for karma in past messages.                             |

## Config

Edit the configuration file located at `config.json`.

| key             | description                                                        | type         | default            |
| --------------- | ------------------------------------------------------------------ | ------------ | ------------------ |
| upvote_emojis   | A list of emojis OR name of server emotes that represent upvotes   | list[string] | ["⬆️", "👆", "👍"] |
| downvote_emojis | A list of emojis OR name of server emotes that represent downvotes | list[string] | ["⬇️", "👇", "👎"] |
| command_prefix  | The command prefix for KarmaBot                                    | string       | ?                  |

## Environment

Environment variables are loaded from a `.env` file.

| key              | value             | required | default |
| ---------------- | ----------------- | -------- | ------- |
| `KARMABOT_TOKEN` | Discord bot token | Yes      | None    |
| `LOG_LEVEL`      | Log level         | No       | INFO    |

## Roadmap

- [x] Karma command
- [x] Persistant karma store (SQLite)
- [ ] Scan previous messages for karma

## License

See [LICENSE](https://github.com/bqrichards/karmabot/blob/main/LICENSE)
