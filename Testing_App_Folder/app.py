#I'm using Shiny Python, I want to change the tab color, increase font-size, visible boundaries of tabs, background color of selected , hover effects. Also add title to dataframe.See code below:

import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
import folium
import shinywidgets
from shiny import reactive
from shiny.express import input, render, ui
import json
import plotly.express as px
from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from htmltools import tags, HTML


# 1. Read local files
app_dir = Path(__file__).parent  # Set environment to local directory

# Dataframe
df = pd.read_csv(app_dir / "dfc_out.csv")

# GeoJSON file
with open(app_dir / "CommunityDistricts.geojson", "r") as f:
    cboard_geo = json.load(f)

# 2. Data preparation
# Prepare time data for filter
df["dateTime"] = pd.to_datetime(df["dateTime"], format='%Y-%m-%d').dt.date
df["index_"] = df["index_"].astype(int)
df["MinutesElapsed"] = df["MinutesElapsed"].astype(float)


# Define community board options
board_options = (
    "All",
    *[f"{str(i).zfill(2)} {borough}" for borough in ["MANHATTAN", "BRONX", "BROOKLYN", "QUEENS", "STATEN ISLAND"] for i in range(1, 13)],
    "26 BRONX",
    "16 BROOKLYN", "17 BROOKLYN", "18 BROOKLYN",
    "13 BROOKLYN", "14 BROOKLYN", "15 BROOKLYN",
    "13 QUEENS", "14 QUEENS"
)

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker() != "All":
        mf = mf[mf["community_board"] == input.ticker()]
    return mf

# Display
ui.page_opts(title="311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem 12/08/24 (View on Desktop)")
ui.nav_spacer()  # Push the navbar items to the right


# Inputting Slideer
with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All")

with ui.nav_panel("Data"):
    ui.include_css(app_dir / "styles.css")
    ui.markdown(
    '''          
            [Updated: 12/6/24] Note: Maps are interactive and click on `Links` for Exploratory Analysis
    '''
    )
    with ui.navset_pill(id="tab"):  
        with ui.nav_panel("Latest 25 Records"):
            def header_text():
                return "**{} Blocked Bike Lane NYPD Response from {} to {}**".format(
                    input.ticker(), input.date_range()[0], input.date_range()[1]
                )

            # Place the dynamic header in the UI
            ui.output_text("header_text")

            @render.data_frame
            def B_df():
                p=['date','Time','incident_address','MinutesElapsed','resolution','resolution_description']
                B= f_df()[p]
                B.columns= ['Date','Time','Address','Response_Mins','Resolution','Description']
                return B.head(25)

        with ui.nav_panel("NYC Response Time HeatMap"):
            ui.markdown(
                '''
                   <div class="flourish-embed flourish-map" data-src="visualisation/20781545"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20781545/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                '''
                )
with ui.nav_panel("About"):
    ui.markdown(
        '''
            ### Purpose
        '''
        )