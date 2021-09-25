import logging
from enum import Enum
from urllib.parse import urlparse

import requests

_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, " \
      "like Gecko) Chrome/87.0.4280.66 Safari/537.36"


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
    PRESENT_OUTSIDE = {
        "MainCode": "02",
        "SecondaryCode": "05"
    }


def _log_response(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response is not None:
            path = urlparse(response.url).path
            if response.ok:
                logging.info(f"Request succeeded [{response.status_code}] - "
                             f"{path}")
            else:
                logging.error(f"Request failed [{response.status_code}] - "
                              f"{path} : {response.text}")

        return response

    return wrapper


class Doh1APIClient:
    def __init__(self, url: str, cookie: str):
        self.url = url
        self.headers = {
            "User-Agent": _ua,
            "cookie": cookie
        }

    def report(self, type_: Report) -> requests.Response:
        logging.info(f"Reporting {type_.name}")
        return self._post(data=type_.value)

    @_log_response
    def _post(self, data: dict = None) -> requests.Response:
        return requests.post(self.url,
                             data=data,
                             headers=self.headers)
