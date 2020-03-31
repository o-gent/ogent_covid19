"""
Flask server to display live(ish) data report
"""

# imports and globals
from flask import Flask


# start flask server
app = Flask(__name__)


@app.route('/')
def index():
    """
    Main report page
    """
    return "this is covid19 central"
