# Python Doh1 API Client

A simple, lightweight piece of code to report doh1.

```
pip install doh1
```

For detailed instructions, read the Automation header.

## Automation

A cronjob, flask application and a telegram bot are provided under the examples
folder.

#### Cronjob

The cronjob is useful as a daily running script to make the report, it loads
the configuration from the `config.json` file.

As written in the module docstring, this is an example for a cron line with its
arguments:

```bash
URL="https://.../InsertPersonalReport"
COOKIE="<LONG-VALUE>"
IFTTT_KEY="<KEY>"
30 5 * * 0-4 $HOME/auto-doh/examples/cronjob.py --url $URL --cookie "$COOKIE" --ifttt-key $IFTTT_KEY >> $HOME/auto-doh/examples/.cronjob.log 2>&1
```

#### Telegram Bot

The telegram bot is useful to view and modify the configuration file remotely.

I use `nohup` to keep the process alive, after I exit the SSH session:

```bash
nohup ./telegram_bot.py >> .telegram_bot.log 2>&1 &
```

<img src="/img/telegram_bot.gif" width="60%" height="60%"/>

#### Flask Application (Deprecated)

The flask application has the same purpose like the Telegram bot but is less
convenient (performing actions through GET requests).
