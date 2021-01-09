import logging
import os
from pathlib import Path

from doh1 import Doh1APIClient, Report

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-8s] - %(message)s""",
                    datefmt="%Y-%m-%d %H:%M:%S""",
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(filename=Path(__file__).parent / "logs.log")
                    ]
                    )

if os.environ.get("DOH1_DISABLE") == "TRUE":
    logging.info("DOH1 is disabled.")
    exit(0)


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


def main():
    report_present()


if __name__ == '__main__':
    main()
