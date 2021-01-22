"""
Cron line:
30 5 * * 0-4 python3 $HOME/auto-doh/examples/cronjob.py --url URL --cookie COOKIE --ifttt-key KEY >> $HOME/auto-doh/examples/_cronjob.log 2>&1
"""

import argparse
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path

import requests

from doh1 import Doh1APIClient, Report

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                    datefmt="%Y-%m-%d %H:%M:%S""")

if os.environ.get("DOH1_DISABLE") == "TRUE":
    logging.info("DOH1 is disabled.")
    exit(0)

SKIP_FILE = Path(__file__).parent / "skipdays.txt"

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True, help="The doh1 API report url")
parser.add_argument("--cookie", required=True, help="The doh1 user cookie (received after passing captcha)")
parser.add_argument("--ifttt-key", dest="ifttt_key",
                    help="The personal IFTTT key is required in order to send notifications")
args = parser.parse_args()


def check_for_skip():
    try:
        with open(SKIP_FILE, 'r') as fh:
            skip_days = fh.read().splitlines()
    except FileNotFoundError:
        return False

    if datetime.now().strftime("%Y-%m-%d") in skip_days:
        logging.info("Skipping today")
        return True
    return False


def random_sleep():
    sleep_time = random.randint(0, 120)
    time.sleep(sleep_time)
    logging.info(f"Woke up from a {sleep_time} seconds sleep")


def notify(status_code: int):
    message = f"Report returned {status_code}"
    response = requests.get(f"https://maker.ifttt.com/trigger/Notify/with/key/{args.ifttt_key}?value1={message}")

    if response.ok:
        logging.info("Successfully alerted using IFTTT")
    else:
        logging.error(f"Failed to alert [{response.status_code}] - {response.text}")


def main():
    if check_for_skip():
        logging.info("Skipping today")
    else:
        random_sleep()

        client = Doh1APIClient(args.url, args.cookie)
        response = client.report(Report.PRESENT)

        if args.ifttt_key is not None:
            notify(response.status_code)
        else:
            logging.info("ifttt-key parameter wasn't passed")


if __name__ == '__main__':
    main()
