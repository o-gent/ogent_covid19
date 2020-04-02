"""
Flask server to display live(ish) data report
"""

# imports and globals
from flask import Flask, render_template, request
from bokeh.embed import components
from plot import deaths_since_start
from datetime import datetime

last_update = datetime.now().strftime("%B %d, %Y %H:%M")

# start flask server
app = Flask(__name__)


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
