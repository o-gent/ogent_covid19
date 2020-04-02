"""
Flask server to display live(ish) data report
"""

# imports and globals
import logging
from datetime import datetime

from bokeh.embed import components
from flask import Flask, render_template, request
from flask.logging import default_handler

from plot import deaths_since_start

last_update = datetime.now().strftime("%B %d, %Y %H:%M")

# start flask server
app = Flask(__name__)

# set up flask logging
class RequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.url = request.url
            record.remote_addr = request.remote_addr
        except:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)

default_handler.setFormatter(formatter)

logging.basicConfig(filename='app_log.log',level=logging.DEBUG)


# begin app code
@app.route('/')
def index():
    """
    Main report page
    Graphs are rendered each time the page is loaded
    """
    # User input for countries
    countries = request.args.get("countries")
    if countries == None:
        # pick some default countries
        countries = []

    # generate plot 1
    script_plot1, div_plot1 = components(deaths_since_start(countries))
    
    # generate plot 2

    # generate plot 3

    return render_template(
        "web.html", 
        script_plot1=script_plot1,  
        div_plot1=div_plot1,
        last_update=last_update
    )


if __name__ == '__main__':
	app.run(port=5000, debug=True)
