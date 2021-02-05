#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, Blueprint

LOGS_PATH = Path(__file__).parent / ".cronjob.log"
CONFIG_FILE = Path(__file__).parent / "config.json"

app = Flask(__name__)
doh_bp = Blueprint("doh", __name__, url_prefix="/doh")

with open(CONFIG_FILE, 'r') as fh:
    config = json.load(fh)


@doh_bp.route("/home")
def home():
    return "Home"


@doh_bp.route("/logs")
def logs():
    try:
        with open(LOGS_PATH, 'r') as fh:
            return "</br>".join(fh.readlines())
    except FileNotFoundError:
        return "FileNotFoundError"


@doh_bp.route("/status")
def status():
    return "Enabled" if config["ENABLED"] else "Disabled"


@doh_bp.route("/disable")
def disable():
    config["ENABLED"] = False
    commit_config()
    return "Disabled"


@doh_bp.route("/enable")
def enable():
    config["ENABLED"] = True
    commit_config()
    return "Enabled"


@doh_bp.route("/skip/<date>")
def skip(date):
    try:
        datetime.strptime(date, "%Y%m%d")
    except ValueError:
        return "Failed to parse date"

    config["SKIP_DAYS"].append(date)
    commit_config()
    return f"Will skip on {date}"


def commit_config():
    with open(CONFIG_FILE, 'w') as fh:
        json.dump(config, fh)


app.register_blueprint(doh_bp)

if __name__ == '__main__':
    app.run("0.0.0.0", port=int(os.environ.get("DOH1_FLASK_PORT", 8050)))
