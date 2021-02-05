"""
Cron line:
30 5 * * 0-4 python3 $HOME/auto-doh/examples/cronjob.py --url URL --cookie COOKIE --ifttt-key KEY >> $HOME/auto-doh/examples/_cronjob.log 2>&1
"""

import argparse
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path

import requests

from doh1 import Doh1APIClient, Report

CONFIG_FILE = Path(__file__).parent / "config.json"

with open(CONFIG_FILE, 'r') as fh:
    config = json.load(fh)


def _configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                        datefmt="%Y-%m-%d %H:%M:%S""")


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="The doh1 API report url")
    parser.add_argument("--cookie", required=True, help="The doh1 user cookie (received after passing captcha)")
    parser.add_argument("--ifttt-key", help="The personal IFTTT key is required in order to send notifications")
    return parser.parse_args()


def check_for_skip():
    if datetime.now().strftime("%Y%m%d") in config["SKIP_DAYS"]:
        logging.info("Skipping today")
        return True
    return False


def random_sleep():
    sleep_time = random.randint(0, 120)
    time.sleep(sleep_time)
    logging.info(f"Woke up from a {sleep_time} seconds sleep")


def notify(status_code: int, ifttt_key: str):
    message = f"Report returned {status_code}"
    response = requests.get(f"https://maker.ifttt.com/trigger/Notify/with/key/{ifttt_key}?value1={message}")

    if response.ok:
        logging.info("Successfully alerted using IFTTT")
    else:
        logging.error(f"Failed to alert [{response.status_code}] - {response.text}")


def main():
    _configure_logging()

    if not config["ENABLED"]:
        logging.info("DOH1 is disabled by environment variable")
        exit(0)

    args = _parse_args()

    if check_for_skip():
        return

    random_sleep()

    client = Doh1APIClient(args.url, args.cookie)
    response = client.report(Report.PRESENT)

    if args.ifttt_key is not None:
        notify(response.status_code, args.ifttt_key)
    else:
        logging.info("ifttt-key parameter wasn't passed")


if __name__ == '__main__':
    main()
