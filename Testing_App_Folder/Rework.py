import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
import folium
import shinywidgets
from shiny import reactive, render, ui
from shiny.express import input, render, ui, session 
import json
import plotly.express as px
from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from htmltools import tags, HTML


#from shiny import App, ui, render,reactive

#1.Read local files 
app_dir = Path(__file__).parent #set environment local
#dataframe
df = pd.read_csv(app_dir / "dfc_out.csv")


#Geofiles
with open(app_dir / "CommunityDistricts.geojson", "r") as f:
    cboard_geo = json.load(f)

#2. Data Prep
#Prepare Time Data for filter
df.dateTime=pd.to_datetime(df['dateTime'], format='%Y-%m-%d')
df.dateTime = df.dateTime.dt.date
df.index_=df.index_.astype(int)
df.MinutesElapsed=df.MinutesElapsed.astype(float)

#board_options= df['cboard_name'].unique()
board_options = ["All"] + sorted(df['cboard_name'].dropna().astype(str).unique())

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker()=='All':
        mf=mf
    else:
        mf=mf[(mf['cboard_name'] == input.ticker())]      
    return mf

# Display
ui.page_opts(title="311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem 12/08/24 (View on Desktop)")
#ui.nav_spacer()  # Push the navbar items to the right


# Inputting Slideer
with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All")
    ui.input_numeric("obs", "Select Min. Entries for Map Display", 5, min=1, max=10) 


#3. Input Options 

ui.include_css(app_dir / "styles.css")
ui.markdown(
'''          
        [Date Updated: 12/17/24]; View Exploratory Data Analysis [HERE](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb)
'''
)
with ui.navset_pill(id="tab"):
    with ui.nav_panel("Summary"):
        with ui.navset_card_underline():
            with ui.nav_panel("Resolution Distribution"):
                @render.plot
                def pieplot1():
                    p2=['resolution','index_']
                    gf=f_df()[p2].groupby(['resolution']).sum().reset_index()
                    gf.columns=['resolution','Count']
                    Total = f_df().index_.sum() 
                    fig=plt.pie(gf.Count, labels=gf.resolution, autopct='%1.0f%%')
                    plt.title('{} NYPD Service Request Resolutions ({} records)'.format(input.ticker(),Total))
                    plt.xlabel('')
                    return fig
    with ui.nav_panel("Interactive Maps"):
        with ui.navset_card_underline():
            with ui.nav_panel("City-Wide NYPD Response HeatMap"):
                ui.markdown(
                    '''
                    <div class="flourish-embed flourish-map" data-src="visualisation/20781545"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20781545/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                    '''
                    )
    

    
    
    with ui.nav_panel("About"):
        ui.markdown(
            '''
                ### Purpose
                * Obstructed bike lanes restricts the use for cyclists, and places them in danger. Greater and timely enforcement deters future violations
                * A diagnosis tool to determine NYPD responses more critically, including their response time 
                * A community dashboard for citizens to CONTINUE to monitor and measure progress of holding NYPD accountable
                ### ABOUT the Dataset
                * Every single record is a 311 request. NYPD is mandated to respond to request. However, there is no external validation that NYPD took action for some cases.
                * The **police response time** is the difference between the opening & closing of the service request. Pay attention to requests ending immediately, and prolonged response.
                * Police resolutions were classified into four categories: Miss, Action, No-Action, and Summons. 
                * Around 75% of service requests led to 'No-Action" or NYPD "Missing" the violators.
                * Learn More in the [data report](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb)
                ### Next Steps
                * The anaylsis can be improved if there is geo-validation to police precinct
                * I'm interested to explore using crowd-source validation as means to verify and hold NYPD accountable. If your a developer, let's chat
                * Partner with local community organizations for an intentional campaign to improve biking violation enforcement.
                ### ABOUT Me
                * I'm trained as an economist (MS Economics in UC Berkeley) and self-learned programmer
                * I'm a community advocate and Jamaica, Queens resident
                * For other data projects, check out my [Github](https://github.com/sustainabu/OpenDataNYC)
                * I'm currently looking for job opportunities feel free to reach out to me (Abu: anayeem1@gmail.com)
            '''
            )
    with ui.nav_menu("Sources"):
        with ui.nav_control():
            ui.a("Exploratory Analysis Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb", target="_blank")
            ui.a("Data Source", href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/", target="_blank")
            ui.a("Github", href="https://github.com/sustainabu/OpenDataNYC/tree/main/311_BlockedBikeLane", target="_blank")

