# get new data from github repository https://github.com/CSSEGISandData/COVID-19
import platform
import subprocess
from functools import lru_cache
# imports and globals
from itertools import cycle
from os.path import join
from typing import List

import bokeh.models
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bokeh.palettes import Colorblind as palette
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from matplotlib.figure import Figure

if platform.system() == "Windows":
    process = subprocess.Popen("cd COVID-19 & git fetch & git pull", stdout=subprocess.PIPE, shell=True)
if platform.system() == "Linux":
    process = subprocess.Popen("cd COVID-19 ; git fetch ; git pull", stdout=subprocess.PIPE, shell=True)
print(process.communicate()[0].strip().decode())


matplotlib.use('Agg')

BASE_DIRECTORY = "COVID-19/csse_covid_19_data/csse_covid_19_time_series"

COUNTRY_DATA = {
    "United Kingdom": {
        "population": 66440000, #2018
        "province": "",
    },
    "France": {
        "population": 66990000, #2019
        "province": "",
    },
    "Germany": {
        "population": 82790000, #2018
        "province": "",
    },
    "Spain": {
        "population":46660000, #2018
        "province": "",
    },
    "Italy" : {
        "population":60480000, #2018
        "province": "",
    },
    "Poland" :{
        "population":37980000, #2018
        "province": "",
    },
    "Norway" : {
        "population": 5368000, #2020
        "province": "",
    },
    "Sweden" : {
        "population" : 10120000, #2018
        "province": "",
    },
    "China" : {
        "population": 59020000, # 2017 just Hubei
        "province": "Hubei",
    },
    "Korea, South": {
        "population": 51470000, #2017
        "province": "",
    },
    "US": {
        "population": 327200000, #2018
        "province": "",
    },
    "New York": {
        "population": 8623000, #2017
        "province": "",
    },
    "India": {
        "population": 1339000000, #2017
        "province": "",
    },
    "Mexico": {
        "population": 129200000, #2017
        "province": "",
    },
    "Iran": {
        "population": 81160000, #2017
        "province": "",
    },
    "Netherlands": {
        "population": 17280000, #2019
        "province": "",
    }
}



# load the datasets
confirmed = pd.read_csv(join(BASE_DIRECTORY, "time_series_covid19_confirmed_global.csv"))
deaths = pd.read_csv(join(BASE_DIRECTORY, "time_series_covid19_deaths_global.csv"))
recovered = pd.read_csv(join(BASE_DIRECTORY, "time_series_covid19_recovered_global.csv"))
# load the US dataset (which is in a different format)
confirmed_US = pd.read_csv(join(BASE_DIRECTORY,"time_series_covid19_confirmed_US.csv"))
deaths_US = pd.read_csv(join(BASE_DIRECTORY,"time_series_covid19_deaths_US.csv"))


def read_us(confirmed_US, deaths_US, state: str):
    global deaths, confirmed
    """
    accept a US formatted dataframe, which could be filtered by state
    """
    confirmed_US_sum = pd.Series()
    deaths_US_sum = pd.Series()

    for column in confirmed_US:
        try:
            confirmed_US_sum[column] = int(confirmed_US[column].sum())
            deaths_US_sum[column] = int(deaths_US[column].sum())

        except Exception as e:
            confirmed_US_sum[column] = ""
            deaths_US_sum[column] = ""
    
    # Need to reformat it a bit
    try:
        confirmed_US_sum = confirmed_US_sum.drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'])
        deaths_US_sum = deaths_US_sum.drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'])
    except:
        # already done
        pass

    confirmed_US_sum['Province/State'] = ""
    confirmed_US_sum['Country/Region'] = state
    confirmed_US_sum['Lat'] = 0
    confirmed_US_sum['Long'] = 0    
    deaths_US_sum['Province/State'] = ""
    deaths_US_sum['Country/Region'] = state
    deaths_US_sum['Lat'] = 0
    deaths_US_sum['Long'] = 0

    # format to df and reorder the columns
    us_deaths = deaths_US_sum.to_frame().T
    us_deaths = us_deaths[deaths.columns]
    us_confirmed = confirmed_US_sum.to_frame().T
    us_confirmed = us_confirmed[confirmed.columns]

    # merge the datasets
    confirmed = pd.concat([confirmed, us_confirmed], ignore_index=True)
    deaths = pd.concat([deaths, us_deaths], ignore_index=True)    
    return confirmed, deaths


# load in US state data
states = ["New York"]
for state in states:
    confirmed, deaths = read_us(confirmed_US[confirmed_US["Province_State"] == state], deaths_US[deaths_US["Province_State"] == state], state)


def load(country: str, state: str) -> pd.DataFrame:
    """
    returns a country as a pandas dataframes with confirmed, deaths, recovered as columns, dates as index
    """
    # could do the following as a loop but eh

    # confirmed
    country_df = confirmed[confirmed['Country/Region'] == country].replace(np.nan, "")
    state_df = country_df[country_df['Province/State'] == state]
    confirmed_result = state_df.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis=1).T

    # deaths
    country_df = deaths[deaths['Country/Region'] == country].replace(np.nan, "")
    state_df = country_df[country_df['Province/State'] == state]
    deaths_result = state_df.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis=1).T

    # recovered
    # try except to deal with US states without recovered data
    try:
        country_df = recovered[recovered['Country/Region'] == country].replace(np.nan, "")
        state_df = country_df[country_df['Province/State'] == state]
        recovered_result = state_df.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis=1).T
        recovered_result[0]
    except:
        recovered_result = deaths_result

    # combine the series to one dataframe
    df_result = pd.concat([confirmed_result, deaths_result, recovered_result], axis =1)
    df_result.columns = ["confirmed", "deaths", "recovered"]
    df_result.index = pd.to_datetime(df_result.index)

    return df_result


# load the data for each country into the dictionary
for country in COUNTRY_DATA.keys():
    # get the data
    df = load(country, COUNTRY_DATA[country]['province'])
    COUNTRY_DATA[country]['data'] = df
    # Normalise data with population figures
    normalise = lambda x: x/COUNTRY_DATA[country]['population'] * 100
    COUNTRY_DATA[country]['normalised_data'] = df.apply(normalise)


# Now we have normalised death values, we need normalised dates. We should only compare counties from the date the virus started killing
# Find the first day of a death for each country
first_day = lambda df: df.deaths[df.deaths <= 0.0001].index[-1]
# need to convert the index to days since the first day
convert_index = lambda df: df[df.index >= first_day(df)].reset_index()


"""
Start graph generation functions
"""

def deaths_since_start(countries: List[str]):
    """
    Plot of deaths as a percentage of population vs days since spread start
    """
    # plot an interactive version using bokeh
    colours = cycle(palette[8])

    fig = figure(
        x_axis_label='Days since deaths started in each country', 
        y_axis_label='Percentage of the population',
        plot_width=800,
        plot_height=500,
        id="plot_1",
        active_drag="pan",
        active_scroll="wheel_zoom",
        )
    
    # add the hover tool and configure it to be useful
    fig.add_tools(bokeh.models.HoverTool())
    hover = fig.select(dict(type=bokeh.models.HoverTool))
    hover.tooltips = [("Country", "@name"), ("Day", "@x"),  ("Value", "@y"),]
    hover.mode = 'mouse'

    for country in countries:
        # convert to days since start 
        series = convert_index(COUNTRY_DATA[country]['normalised_data']).deaths
        label = country + " " + COUNTRY_DATA[country]['province']
        # create a bokeh data source
        source = ColumnDataSource({
            'x' : series.index,
            'y' : series.values,
            'name' : [label for x in series.index],
        })

        fig.line(
            'x', 
            'y', 
            source=source,
            legend_label=country, 
            line_width=2, 
            color=next(colours)
        )

    return fig


def deaths_since_start_mobile(countries: List[str]):
    """
    Matplotlib version of bokeh plot
    """
    fig = Figure(figsize=(10,6))
    ax = fig.add_subplot(1, 1, 1)

    for country in countries:
        ax.plot(convert_index(COUNTRY_DATA[country]['normalised_data']).deaths)
    
    ax.legend([country + " " + COUNTRY_DATA[country]['province'] for country in countries])
    ax.set_xlim([0, 40])
    ax.set_xlabel("Days since spread started in each country")
    ax.set_ylabel("Percentage of the population")

    # set the font size
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(18)

    return fig


@lru_cache()
def acceleration(country):
    """
    get the accelation of deaths and confimred cases for a country
    """
    # confirmed
    df = COUNTRY_DATA[country]['data'].confirmed.diff()
    df = df[df.index > (pd.Timestamp.now() - pd.Timedelta(days=8))]
    bestfit = np.polyfit(x=range(len(df.values)), y=df.values, deg=1)
    confirmed_gradient = bestfit[0] / COUNTRY_DATA[country]['population']
    
    # deaths
    df = COUNTRY_DATA[country]['data'].deaths.diff()
    df = df[df.index > (pd.Timestamp.now() - pd.Timedelta(days=8))]
    bestfit = np.polyfit(x=range(len(df.values)), y=df.values, deg=1)
    deaths_gradient = bestfit[0] / COUNTRY_DATA[country]['population']
    
    return confirmed_gradient, deaths_gradient


def acceleration_deaths_plot(countries: List[str]):
    # make bar charts with accerlation/sum for confirmed/deaths for each country
    # do with matplotlib as bokeh is being a bitch
    # stacked example
    deaths_accel = [acceleration(country)[1] for country in countries]

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    # set width of bar
    barWidth = 0.8
    
    # Set position of bar on X axis
    r1 = np.arange(len(deaths_accel))
    
    # Make the plot
    axis.bar(r1, deaths_accel, color='#8f0000', width=barWidth, edgecolor='white', label='confirmed cases')
    
    # Add xticks on the middle of the group bars
    axis.set_xlabel('Country/State', fontweight='bold')
    axis.set_ylabel("acceleration of deaths (% of population)")
    axis.set_xticks(np.arange(len(countries)))
    axis.set_xticklabels(countries)
    axis.axhline(0, color='black')
    minimum = lambda x: min(x)*1.3 if min(x) < 0 else 0
    maximum = lambda x: max(x)*1.3 if max(x) > 0 else 0
    axis.set_ylim(bottom=minimum(deaths_accel)*1.3, top=maximum(deaths_accel) * 1.3)

    fig.set_size_inches(10,7)

    fig.tight_layout()

    return fig

def acceleration_confirmed_plot(countries: List[str]):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    # set width of bar
    barWidth = 0.8
    
    # set height of bar
    confirmed_accel = [acceleration(country)[0] for country in countries]
    
    # Set position of bar on X axis
    r1 = np.arange(len(confirmed_accel))
    
    # Make the plot
    axis.bar(r1, confirmed_accel, color='#537599', width=barWidth, edgecolor='white', label='confirmed cases')
    
    # Add xticks on the middle of the group bars
    axis.set_xlabel('Country/State', fontweight='bold')
    axis.set_ylabel("acceleration of confirmed cases (% of population)")
    axis.set_xticks(np.arange(len(countries)))
    axis.set_xticklabels(countries)
    #axis.set_xticks(rotation=90)
    axis.axhline(0, color='black')

    minimum = lambda x: min(x)*1.3 if min(x) < 0 else 0
    maximum = lambda x: max(x)*1.3 if max(x) > 0 else 0
    axis.set_ylim(bottom=minimum(confirmed_accel)*1.3, top=maximum(confirmed_accel) * 1.3)

    fig.set_size_inches(10,7)

    return fig


def summary_table(countries: List[str]):
    """
    Total confirmed, total deaths, acceleration absolute
    """
    
    df_list = []
    
    # add headers
    df_list.append(
        [
            "Country",
            "Confirmed cases",
            "Confirmed acceleration",
            "Deaths",
            "Deaths acceleration"
        ]
    )
    
    for country in countries:
        acceleration_figures = acceleration(country)
        pop = COUNTRY_DATA[country]['population']
        df_list.append(
            [
                country,
                COUNTRY_DATA[country]['data'].confirmed[-1],
                int(acceleration_figures[0] * pop),
                COUNTRY_DATA[country]['data'].deaths[-1],
                int(acceleration_figures[1] * pop),
            ]
        )

    return df_list

