import os
from pathlib import Path

from flask import Flask, Blueprint

LOGS_PATH = Path(__file__).parent / "logs.log"

app = Flask(__name__)
doh_bp = Blueprint("doh", __name__, url_prefix="/doh")


@doh_bp.route("/")
@doh_bp.route("/home")
def home():
    return "Home"


@doh_bp.route("/logs")
def logs():
    try:
        with open(LOGS_PATH, 'r') as fh:
            return fh.read()
    except FileNotFoundError:
        return "FileNotFoundError"


@doh_bp.route("/status")
def status():
    if os.environ.get("DOH1_DISABLE") == "TRUE":
        return "Status: Disabled"
    return "Status: Enabled"


@doh_bp.route("/disable")
def disable():
    os.environ["DOH1_DISABLE"] = "TRUE"
    return "Disabled"


@doh_bp.route("/enable")
def enable():
    try:
        del os.environ["DOH1_DISABLE"]
    except KeyError:
        pass
    return "Enabled"


app.register_blueprint(doh_bp)

if __name__ == '__main__':
    app.run("0.0.0.0", port=int(os.environ.get("DOH1_FLASK_PORT", 8050)))
