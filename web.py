"""
Flask server to display live(ish) data report
"""

import io
# imports and globals
import logging
from datetime import datetime
import time

from bokeh.embed import components
from flask import Flask, Response, render_template, request, redirect, abort
from flask.logging import default_handler
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

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

BANNED = ["118.172.154.178"]
@app.before_request
def block():
    if request.remote_addr in BANNED:
        abort(403)


@app.after_request
def after_request(response):
    # log usage data
    logging.info(f"{datetime.now():%Y-%m-%d %H:%M:%S%z} | {request.remote_addr} | {request.url} | {request.user_agent.platform}")

    # lets troll
    if not app.debug:
        if request.url.startswith("http://146.148.32.5"):
            time.sleep(10)
            logging.info("redirecting an IP URL")
            return redirect("http://90.207.238.183")
        # for some reason we get a bunch of these
        elif request.url == "http://covid-19/":
            time.sleep(60)
        # just capture all cases too
        elif not (request.url.startswith("http://ogent.uk") or request.url.startswith("http://bettercovid19data.com")):
            time.sleep(10)
            logging.info("redirecting a non o-gent url")
            return redirect("http://www.google.com")
    else:
        logging.info("app is in debug mode")
        
    return response


# begin app code
@app.route('/')
def index():
    """
    Main report page
    Graphs are rendered each time the page is loaded
    """

    # User input for countries
    countries = []
    if request.args.get("All") == "on":
        countries = plot.COUNTRY_DATA.keys()
    else:
        for country in plot.COUNTRY_DATA.keys():
            if request.args.get(country) == "on":
                countries.append(country)
    if countries == []:
        countries = ["United Kingdom", "France", "Germany", "Spain"] # pick some default countries
    
    # generate the GET parameters for other plots
    param = "?"
    for country in countries:
        param += country + "=on&"
    param = param.replace(" ", "+")

    
    show_all = request.args.get("Table_all")
    if show_all == "on":
        summary_table = plot.summary_table(plot.sorted_countries())
    else:
        summary_table = plot.summary_table(plot.sorted_countries()[0:10])

    # Render desktop version or mobile version
    # Not ideal but necessary due to matplotlib and bokeh limitations
    mobile = ["android", "iphone"]
    if request.user_agent.platform in mobile:
        

        return render_template(
            "web.html",
            mobile=True,
            script_plot1="",
            div_plot1="",
            last_update=last_update,
            param=param,
            table=summary_table
        )

    else:
        # generate plot 1
        script_plot1, div_plot1 = components(plot.deaths_since_start(countries))

        return render_template(
            "web.html", 
            script_plot1=script_plot1,  
            div_plot1=div_plot1,
            last_update=last_update,
            param=param,
            table=summary_table
        )


# Matplotlib serving section

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


@app.route('/acceleration_deaths_plot_mobile.png')
def accelation_deaths_mobile():
    """
    MOBILE VERSION
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

    # increase font size
    ax = fig.axes[0]
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(18)
    
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


@app.route('/acceleration_confirmed_plot_mobile.png')
def accelation_confirmed_mobile():
    """
    MOBILE VERSION
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
    
    # increase font size
    ax = fig.axes[0]
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(18)
    # output the figure as a response
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output, bbox_inches='tight')
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/deaths_since_start_mobile.png')
def deaths_since_start_mobile():
    """
    MOBILE VERSION
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
    fig = plot.deaths_since_start_mobile(countries)

    # make room for labels
    fig.subplots_adjust(bottom=0.15)

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
