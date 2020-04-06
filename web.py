"""
Flask server to display live(ish) data report
"""

# imports and globals
import logging
from datetime import datetime

from bokeh.embed import components
from flask import Flask, render_template, request
from flask.logging import default_handler

import plot

last_update = datetime.now().strftime("%B %d, %Y %H:%M")

# start flask app
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

logging.basicConfig(filename='app_log.log',level=logging.INFO)
logging.FileHandler('app_log.log', mode='a')

root = logging.getLogger()
root.addHandler(default_handler)


# begin app code
@app.route('/')
def index():
    """
    Main report page
    Graphs are rendered each time the page is loaded
    """
    logging.info(f"{datetime.now():%Y-%m-%d %H:%M:%S%z} | {request.remote_addr} | {request.url}")

    # User input for countries
    countries = []
    for country in plot.COUNTRY_DATA.keys():
        if request.args.get(country) == "on":
            countries.append(country)
    if countries == []:
        # pick some default countries
        countries = ["United Kingdom", "New York"]


    # generate plot 1
    script_plot1, div_plot1 = components(plot.deaths_since_start(countries))

    # generate the GET parameters for other plots
    param = "?"
    for country in countries:
        param += country + "=on&"
    param = param.replace(" ", "+")

    return render_template(
        "web.html", 
        script_plot1=script_plot1,  
        div_plot1=div_plot1,
        last_update=last_update,
        countries = list(plot.COUNTRY_DATA.keys()),
        param=param
    )

# Matplotlib serving section
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
from flask import Response


@app.route('/acceleration_deaths_plot.png')
def accelation_deaths():
    """
    Countries as GET paramters
    """
    # handle input
    countries = []
    for country in plot.COUNTRY_DATA.keys():
        if request.args.get(country) == "on":
            countries.append(country)
    if countries == []:
        # pick some default countries
        countries = ["United Kingdom", "New York"]  

    # get the figure
    fig = plot.acceleration_deaths_plot(countries)
    # output the figure as a response
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output, bbox_inches='tight')
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/acceleration_confirmed_plot.png')
def accelation_confirmed():
    """
    Countries as GET paramters
    """
    # handle input
    countries = []
    for country in plot.COUNTRY_DATA.keys():
        if request.args.get(country) == "on":
            countries.append(country)
    if countries == []:
        # pick some default countries
        countries = ["United Kingdom", "New York"]  

    # get the figure
    fig = plot.acceleration_confirmed_plot(countries)
    # output the figure as a response
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output, bbox_inches='tight')
    return Response(output.getvalue(), mimetype='image/png')


# app maintanance section
@app.route('/update')
def update():
    """
    update data sources on load
    """
    global last_update
    global plot
    last_update = datetime.now().strftime("%B %d, %Y %H:%M")
    from importlib import reload 
    reload(plot)
    return "updated!"



if __name__ == '__main__':
    # start the flask server
	app.run(port=5000, debug=True)
