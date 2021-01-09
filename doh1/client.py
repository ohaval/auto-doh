import logging
import re
from enum import Enum

import requests


class Report(Enum):
    PRESENT = {
        "MainCode": "01",
        "SecondaryCode": "01"
    }
    DAY_OFF = {
        "MainCode": "04",
        "SecondaryCode": "01",
        "Note": None
    }


def _log_response(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response is not None:
            path = re.search(r"https?://.*?(/.*)", response.url).group(1)
            if response.ok:
                logging.info(f"Request succeeded [{response.status_code}] - {path}")
            else:
                logging.error(f"Request failed [{response.status_code}] - {path} : {response.text}")

        return response

    return wrapper


class Doh1APIClient:
    def __init__(self, url: str, cookie: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.66 Safari/537.36",
            "cookie": cookie
        }

    @_log_response
    def _post(self, data: dict = None) -> requests.Response:
        return requests.post(self.url,
                             data=data,
                             headers=self.headers)

    def report(self, type_: Report) -> requests.Response:
        logging.info(f"Reporting {type_.name}")
        return self._post(data=type_.value)