#!/usr/bin/env python3
"""A cronjob script to report doh1 daily

Cron line example:
30 5 * * 0-4 $HOME/auto-doh/examples/cronjob.py --url URL --cookie "COOKIE" --ifttt-key KEY >> $HOME/auto-doh/examples/.cronjob.log 2>&1  # noqa: E501
"""

import argparse
import json
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

from doh1 import Doh1APIClient, Report

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                    datefmt="%Y-%m-%d %H:%M:%S""")

CONFIG_FILE = Path(__file__).parent / "config.json"

with open(CONFIG_FILE, "r") as fh:
    config = json.load(fh)


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
    if datetime.now().strftime("%Y%m%d") in config["SKIP_DAYS"]:
        logging.info("Skipping today")
        return True
    return False


def random_sleep(sleep_time: int):
    sleep_time = random.randint(0, sleep_time)
    time.sleep(sleep_time)
    logging.info(f"Woke up from a {sleep_time} seconds sleep")


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
    if not config["ENABLED"]:
        logging.info("DOH1 is disabled by environment variable")
        sys.exit()

    args = _parse_args()

    if check_for_skip():
        return

    random_sleep(args.sleep_time)

    client = Doh1APIClient(args.url, args.cookie)
    response = client.report(Report.PRESENT)

    if args.ifttt_key is not None:
        notify(args.ifttt_key,
               message=f"Report returned {response.status_code}")


if __name__ == "__main__":
    main()
