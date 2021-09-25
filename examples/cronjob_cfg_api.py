"""This module exposes a list of methods to view data and manage the config

The configuration file is 'config.json' and it's content is loaded into the
'config' variable (dictionary).
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Union

CONFIG_FILE = Path(__file__).parent / "config.json"

date_fmt = "%d/%m/%Y"


def _get_config() -> dict:
    with open(CONFIG_FILE, "r") as fh:
        return json.load(fh)


config = _get_config()


def commit_config(func):
    def wrapper(*args, **kwargs):
        rv = func(*args, **kwargs)

        with open(CONFIG_FILE, "w") as fh:
            json.dump(config, fh)

        return rv

    return wrapper


def is_enabled() -> bool:
    return config["ENABLED"]


@commit_config
def enable() -> None:
    config["ENABLED"] = True


@commit_config
def disable() -> None:
    config["ENABLED"] = False


def get_skipdates(as_date: bool = False) -> List[Union[str, date]]:
    """Returns all skipdates in a list of type 'date' or 'str'."""
    if as_date:
        return [datetime.strptime(date_, date_fmt).date()
                for date_ in config["SKIP_DATES"]]

    return config["SKIP_DATES"]


@commit_config
def add_skipdate(skipdate: date) -> None:
    config["SKIP_DATES"].append(skipdate.strftime(date_fmt))

    # Keep the list unique and sorted
    config["SKIP_DATES"] = list(set(config["SKIP_DATES"]))
    config["SKIP_DATES"].sort(key=lambda d: datetime.strptime(d, "%d/%m/%Y"))


def filter_skipdates_from_date(skipdates: List[date],
                               date_: date) -> List[date]:
    """Filters skipdates with items earlier than the provided date"""
    return [skipdate for skipdate in skipdates if skipdate >= date_]


def format_with_weekday(date_: date, markdownv2: bool = False) -> str:
    """Returns a string of the date followed by the weekday inside parentheses

    When the markdownv2 optional parameter is set to True, the returned string
    is returned with escaped characters.
    """
    if markdownv2:
        return date_.strftime(fr"{date_fmt} \(%A\)")
    return date_.strftime(fr"{date_fmt} (%A)")
