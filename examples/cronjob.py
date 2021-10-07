#!/usr/bin/env python3
"""A cronjob script to report doh1 daily.

Cron line example:
30 5 * * 0-4 $HOME/auto-doh/examples/cronjob.py --url URL --cookie "COOKIE" --ifttt-key KEY >> $HOME/auto-doh/examples/.cronjob.log 2>&1  # noqa: E501
"""

import argparse
import logging
import random
import time
from datetime import date

import requests

import cronjob_cfg_api as cron_cfg
from doh1 import Doh1APIClient, Report

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                    datefmt="%Y-%m-%d %H:%M:%S""")


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="The doh1 API report url")
    parser.add_argument("--cookie", required=True,
                        help="The doh1 user cookie (received after passing "
                             "captcha)")
    parser.add_argument("--ifttt-key",
                        help="The personal IFTTT key is required in order to "
                             "send notifications")
    parser.add_argument("--sleep-time", type=int, default=600,
                        help="The maximum amount of seconds to sleep before "
                             "reporting (default %(default)s)")

    args = parser.parse_args()
    logging.info(f"Provided args: {args}")
    return args


def check_for_skip():
    return date.today() in cron_cfg.get_skipdates(as_date=True)


def random_sleep(max_sleep_time: int):
    time.sleep(random.randint(0, max_sleep_time))
    logging.info(f"Woke up from a {max_sleep_time} seconds sleep")


def notify(ifttt_key: str, message: str):
    try:
        response = requests.get(
            f"https://maker.ifttt.com/trigger/Notify/with/key/{ifttt_key}?value1={message}")  # noqa

    except requests.RequestException:
        logging.info("Failed to send GET request to IFTTT", exc_info=True)
    else:
        if response.ok:
            logging.info("Successfully alerted using IFTTT")
        else:
            logging.error("Failed to alert using IFTTT (received "
                          f"{response.status_code}) - {response.text}")


def main():
    args = _parse_args()

    if not cron_cfg.is_enabled():
        logging.info("DOH1 is disabled by environment variable")
        return

    if check_for_skip():
        logging.info("Skipping today")
        return

    random_sleep(args.sleep_time)

    client = Doh1APIClient(args.url, args.cookie)
    response = client.report(Report.PRESENT)

    if args.ifttt_key is not None:
        notify(args.ifttt_key,
               message=f"Report returned {response.status_code}")


if __name__ == "__main__":
    main()
