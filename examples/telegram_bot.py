#!/usr/bin/env python3
"""A telegram bot to control, and view information remotely on a doh1 cronjob

Manually edit the 'TOKEN' variable with the API token, or set the
'DOH1_BOT_TOKEN' environment variable.

Use nohup to run without hangups:
nohup ./telegram_bot.py >> .telegram_bot.log 2>&1 &
"""

import logging
import os
from datetime import date, datetime, timedelta

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, MessageHandler, Filters,
    CallbackQueryHandler
)

import cronjob_cfg_api as cron_cfg

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                    datefmt="%Y-%m-%d %H:%M:%S""")

TOKEN = os.environ["DOH1_BOT_TOKEN"]


def help_(update: Update, context: CallbackContext) -> None:
    text = r"""
__HELP__

/start
*Start the buttons menu* \(has most functionality\)

/skip %d/%m/%Y
Skip a *specific date*

/list\_all\_skipdates
View *all* skipdates

/help
View this help message
"""
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


def start(update: Update, context: CallbackContext) -> None:
    text = "Choose:"
    keyboard = [
        [InlineKeyboardButton("Offer skipdates",
                              callback_data="OFFER_SKIPDATES")],
        [
            InlineKeyboardButton("Check skipdates",
                                 callback_data="LIST_SKIPDATES"),
            InlineKeyboardButton("Check status",
                                 callback_data="CHECK_STATUS")
        ],
        [
            InlineKeyboardButton("Enable", callback_data="ENABLE"),
            InlineKeyboardButton("Disable", callback_data="DISABLE"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # When '/start' is sent
    if update.message is not None:
        update.message.reply_text(text, reply_markup=reply_markup)

    # When a button is used to go back to this menu
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(text, reply_markup=reply_markup)


def list_all_skipdates(update: Update, context: CallbackContext) -> None:
    """Sends a message to the user with all skipdates listed"""

    text = """__All skipdates__
    """
    for skipdate in cron_cfg.get_skipdates(as_date=True):
        text = "\n".join(
            [text, cron_cfg.format_with_weekday(skipdate, markdownv2=True)]
        )

    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


def skip(update: Update, context: CallbackContext) -> None:
    """Adds to the skip dates list the provided date.

    This function also handles edge cases when no argument is provided, the
    provided date is in bad format or when the date has already passed.
    """
    if not context.args:
        context.bot.send_message(update.effective_chat.id,
                                 "No argument received, send '/skip %d/%m/%Y'")
        return

    try:
        skipdate = datetime.strptime(context.args[0], cron_cfg.date_fmt)

    except (TypeError, ValueError):
        context.bot.send_message(update.effective_chat.id,
                                 "Enter a date in the right format (%d/%m/%Y)")
        return

    skipdate = skipdate.date()

    if skipdate < date.today():
        context.bot.send_message(update.effective_chat.id,
                                 "Date received has already passed")
        return

    cron_cfg.add_skipdate(skipdate)
    context.bot.send_message(update.effective_chat.id,
                             f"Added {context.args[0]} to skipdates")


def button(update: Update, context: CallbackContext) -> None:
    """Handles CallbackContext coming from button clicks"""
    query = update.callback_query
    query.answer()

    if query.data == "CHECK_STATUS":
        status = "Enabled" if cron_cfg.is_enabled() else "Disabled"
        query.edit_message_text(f"Status is *{status}*",
                                parse_mode=ParseMode.MARKDOWN_V2)

    elif query.data == "ENABLE":
        cron_cfg.enable()
        query.edit_message_text("*Enabled* successfully",
                                parse_mode=ParseMode.MARKDOWN_V2)

    elif query.data == "DISABLE":
        cron_cfg.disable()
        query.edit_message_text("*Disabled* successfully",
                                parse_mode=ParseMode.MARKDOWN_V2)

    elif query.data == "LIST_SKIPDATES":
        _list_skipdates(update, context)

    elif query.data == "OFFER_SKIPDATES":
        _offer_skipdates(update, context)

    elif query.data == "MENU":
        start(update, context)

    elif query.data.startswith("SKIPDATE_"):
        query.delete_message()
        context.args = [query.data.split("_")[1]]
        skip(update, context)


def _list_skipdates(update: Update, context: CallbackContext) -> None:
    """Lists (sends a message) skipdates ahead and from the last 10 days"""

    text = r"""__Skipdates__
    """
    skipdates = cron_cfg.get_skipdates(as_date=True)
    filtered_skipdates = cron_cfg.filter_skipdates_from_date(
        skipdates=skipdates, date_=date.today() - timedelta(days=10)
    )

    for skipdate in filtered_skipdates:
        text = "\n".join(
            [text, cron_cfg.format_with_weekday(skipdate, markdownv2=True)]
        )

    update.callback_query.edit_message_text(text,
                                            parse_mode=ParseMode.MARKDOWN_V2)


def _offer_skipdates(update: Update, context: CallbackContext) -> None:
    """Offers to the telegram client the next 2 * 4 possible dates to skip.

    Instead of showing every option in it's own line, show 2 options in
    every line. That's why the construction of the keyboard is needed.
    The final keyboard list will look like:
    [
        [a, b],
        [c, d],
        [e, f],
        [g, h]
    ]
    It's possible to modify the value of the items (per line or total count),
    but I have found those values to fit perfect on a regular smartphone.
    """
    items_per_line = 2
    items_count = items_per_line * 4

    keyboard = [[] for _ in range(items_count // items_per_line)]

    def get_button(date_: date):
        return InlineKeyboardButton(
            text=cron_cfg.format_with_weekday(date_),
            callback_data=f"SKIPDATE_{date_.strftime(cron_cfg.date_fmt)}"
        )

    def insert(button_: InlineKeyboardButton):
        for row in keyboard:
            if len(row) < items_per_line:
                row.append(button_)
                return

    i = 0
    while len(keyboard[items_count // items_per_line - 1]) != items_per_line:
        date_to_offer = date.today() + timedelta(days=i)
        i += 1

        if date_to_offer.weekday() not in (4, 5):  # Friday or Saturday
            insert(get_button(date_to_offer))

    keyboard.append([InlineKeyboardButton("Menu", callback_data="MENU")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text="Choose one of the following days to skip, "
             "or use /skip %d.%m.%Y to skip a specific day",
        reply_markup=reply_markup
    )


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("skip", skip))
    dispatcher.add_handler(CommandHandler("list_all_skipdates",
                                          list_all_skipdates))
    dispatcher.add_handler(CommandHandler("help", help_))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                          help_))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
