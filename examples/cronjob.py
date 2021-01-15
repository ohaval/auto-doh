import logging
import os
from datetime import datetime
from pathlib import Path

import requests

from doh1 import Doh1APIClient, Report

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                    datefmt="%Y-%m-%d %H:%M:%S""",
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(filename=Path(__file__).parent / "_cronjob.log")
                    ]
                    )

if os.environ.get("DOH1_DISABLE") == "TRUE":
    logging.info("DOH1 is disabled.")
    exit(0)

SKIP_FILE = Path(__file__).parent / "skipdays.txt"
IFTTT_KEY = os.environ.get("IFTTT_KEY")


class MissingEnvironmentVariableException(Exception):
    pass


def report_present():
    client = get_client_from_env()
    return client.report(Report.PRESENT)


def get_client_from_env():
    _validate_env()
    return Doh1APIClient(os.environ["DOH1_URL"], os.environ["DOH1_COOKIE"])


def _validate_env():
    for var in ("DOH1_URL", "DOH1_COOKIE"):
        if var not in os.environ:
            message = f"{var} is missing as an environment variable."
            logging.error(message)
            raise MissingEnvironmentVariableException(message)


def _check_for_skip():
    try:
        with open(SKIP_FILE, 'r') as fh:
            skip_days = fh.read().splitlines()
    except FileNotFoundError:
        return False

    if datetime.now().strftime("%Y-%m-%d") in skip_days:
        logging.info("Skipping today")
        return True
    return False


def notify(status_code: int):
    message = f"Report returned {status_code}"
    response = requests.get(f"https://maker.ifttt.com/trigger/Notify/with/key/{IFTTT_KEY}?value1={message}")

    if response.ok:
        logging.info("Successfully alerted using IFTTT")
    else:
        logging.error(f"Failed to alert [{response.status_code}] - {response.text}")


def main():
    if not _check_for_skip():
        response = report_present()
        if IFTTT_KEY is not None:
            notify(response.status_code)
        else:
            logging.info("IFTTT_KEY environment variable wasn't set")


if __name__ == '__main__':
    main()
