# imports and globals
from itertools import cycle
from os.path import join
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bokeh.palettes import Colorblind as palette
from bokeh.plotting import figure, output_file, show
import bokeh.models

BASE_DIRECTORY = "COVID-19\\csse_covid_19_data\\csse_covid_19_time_series\\"

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
    "China" : {
        "population": 59020000, # 2017 just Hubei
        "province": "Hubei",
    },
    "Korea, South": {
        "population": 51470000, #2017
        "province": "",
    }
}


# load the datasets
confirmed = pd.read_csv(join(BASE_DIRECTORY, "time_series_covid19_confirmed_global.csv"))
deaths = pd.read_csv(join(BASE_DIRECTORY, "time_series_covid19_deaths_global.csv"))
recovered = pd.read_csv(join(BASE_DIRECTORY, "time_series_covid19_recovered_global.csv"))

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
    country_df = recovered[recovered['Country/Region'] == country].replace(np.nan, "")
    state_df = country_df[country_df['Province/State'] == state]
    recovered_result = state_df.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis=1).T

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
    hover.tooltips = [("Country", "@series_name"), ("Day", "@x"),  ("Value", "@y"),]
    hover.mode = 'mouse'

    for country in COUNTRY_DATA.keys():
        series = convert_index(COUNTRY_DATA[country]['normalised_data']).deaths
        fig.line(series.index, series.values, legend_label=country, line_width=2, color=next(colours))

    return fig


