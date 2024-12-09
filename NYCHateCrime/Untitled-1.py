import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
import folium
import shinywidgets
from shiny import reactive
from shiny.express import input, render, ui, session
import json
import branca
import geopandas
import plotly.express as px
from shinywidgets import render_plotly
import matplotlib.pyplot as plt




#0.Note- Operating env required to "pip3 install numpy" to run
#Title
#ui.panel_title("NYC Hate Crimes Dashboard", "Window title")


#1.Read local files 
app_dir = Path(__file__).parent #set environment local
#dataframe
df = pd.read_csv(app_dir / "dfc_out.csv")
#Geofiles
with open(app_dir / "CommunityDistricts.geojson", "r") as f:
    cboard_geo = json.load(f)
#CSS files

#2. Data Prep
#Prepare Time Data for filter
df.dateTimeO=pd.to_datetime(df['dateTimeO'], format='%Y-%m-%d')
df.dateTimeO = df.dateTimeO.dt.date
#GeOMAPPING
df.cboard=df.cboard.astype(str)  #needed for proper merge
state= geopandas.GeoDataFrame.from_features(cboard_geo, crs="EPSG:4326")
d=['geometry','boro_cd']
state= state[d]
state.columns=['geometry','cboard']
#Input Variable Options
board_options= ('All',"01 MANHATTAN", "02 MANHATTAN", "03 MANHATTAN", "04 MANHATTAN", "05 MANHATTAN", "06 MANHATTAN", "07 MANHATTAN", "08 MANHATTAN", "09 MANHATTAN", "10 MANHATTAN", "11 MANHATTAN", "12 MANHATTAN", "01 BRONX", "02 BRONX", "03 BRONX", "04 BRONX", "05 BRONX", "06 BRONX", "07 BRONX", "08 BRONX", "09 BRONX", "11 BRONX", "12 BRONX", "26 BRONX", "01 BROOKLYN", "02 BROOKLYN", "03 BROOKLYN", "04 BROOKLYN", "05 BROOKLYN", "06 BROOKLYN", "07 BROOKLYN", "08 BROOKLYN", "09 BROOKLYN", "10 BROOKLYN", "13 BROOKLYN", "14 BROOKLYN", "15 BROOKLYN", "18 BROOKLYN", "01 QUEENS", "02 QUEENS", "03 QUEENS", "04 QUEENS", "05 QUEENS", "06 QUEENS", "07 QUEENS", "11 QUEENS", "12 QUEENS", "14 QUEENS")

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTimeO"] >= input.date_range()[0]) & (df["dateTimeO"] <= input.date_range()[1])]
    if input.ticker()=='All':
        mf=mf
    else:
        mf=mf[(mf['community_board'] == input.ticker())]      
    return mf

# Secondary Reactive
#@reactive.calc
#def f_dfb():
#    mf = df[(df["dateTimeO"] >= input.date_range()[0]) & (df["dateTimeO"] <= input.date_range()[1])]
#    return mf


#6 Inputting Options

# Display
ui.page_opts(title="311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem 12/08/24 (View on Desktop)")
ui.nav_spacer()  # Push the navbar items to the right

with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All")
    ui.input_numeric("obs", "Minimum Service Request", 5, min=1, max=10) 


    
