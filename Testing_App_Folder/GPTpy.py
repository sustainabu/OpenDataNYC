import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
import folium
import shinywidgets
from shiny import reactive
from shiny.express import input, render, ui, session
import json
import plotly.express as px
from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from htmltools import tags, HTML

#1.Read local files 
app_dir = Path(__file__).parent #set environment local
#dataframe
df = pd.read_csv(app_dir / "dfc_out.csv")

#2. Data Prep
#Prepare Time Data for filter
df.dateTime=pd.to_datetime(df['dateTime'], format='%Y-%m-%d')
df.dateTime = df.dateTime.dt.date
df.index_=df.index_.astype(int)
df.MinutesElapsed=df.MinutesElapsed.astype(float)

board_options = ["All"] + sorted(df['cboard_name'].dropna().astype(str).unique())



#Test CSS
df_styles = [
    {
        "location": "body",
        "style": {
            "border": "0.5px solid black"
        },
    },
    {
        "location": "body",
        "rows": [0,2],
        "style": {
            "background-color": "#FFE5B4",
        },
    },
    {
        "location": "body",
        "rows": [1,3],
        "style": {
            "background-color": "#f4ebfe",
        },
    },
    {
        "location": "body",
        "rows": [4],
        "style": {
            "background-color": "yellow",
        },
    },
        {
        "location": "body",
        "cols": [2,3,4,5,6,7,8],
        "style": {
            "text-align": "right",
        },
    },
        {
        "location": "body",
        "cols": [0],
        "style": {
            "font-weight": "bold",
        },
    },
]

#Test CSS
df_styles1 = [
    {
        "location": "body",
        "style": {
            "border": "0.5px solid black"
        },
    },
    {
        "location": "body",
        "rows": [0,2,4,6,8,10,12,14,16,18,20,22,24],
        "style": {
            "background-color": "#FFE5B4",
        },
    },
    {
        "location": "body",
        "rows": [1,3,5,7,9,11,13,15,17,19,21,23],
        "style": {
            "background-color": "#f4ebfe",
        },
    },
    {
        "location": "body",
        "cols": [3,4],
        "style": {
            "text-align": "right",
        },
    },
    {
        "location": "body",
        "cols": [5],  # Target the 6th column (index 5)
        "style": {
            "width": "300px",  # Adjust the width as needed
            "white-space": "normal",  # Allow text wrapping if necessary
        },
    },
]

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker() != "All":
        mf = mf[mf["cboard_name"] == input.ticker()]
    return mf




# Display
ui.page_opts(title="311 Blocked Bike Lane Dashboard")
ui.nav_spacer()  # Push the navbar items to the right


# Inputting Slideer
with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All")
    ui.input_numeric("obs", "Select Min. Entries for Map Display", 3, min=1, max=10) 


#3. Input Options 


with ui.nav_panel("Dashboard"):
    ui.include_css(app_dir / "styles.css")
    ui.markdown(
    '''          
            [Date Updated: 12/17/24]; View Exploratory Data Analysis [HERE](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb)
    '''
    )
    with ui.navset_pill(id="tab"):
        with ui.nav_panel("Data"):
            with ui.navset_card_underline():
                with ui.nav_panel("Resolution Distribution"):
                    @render.plot
                    def pieplot1():
                        p2=['resolution','index_']
                        gf=f_df()[p2].groupby(['resolution']).sum().reset_index()
                        gf.columns=['resolution','Count']
                        Total = f_df().index_.sum() 
                        fig=plt.pie(gf.Count, labels=gf.resolution, autopct='%1.0f%%')
                        plt.title('{} NYPD Blocked Bike Lane Resolution ({} records)'.format(input.ticker(),Total))
                        plt.xlabel('')
                        return fig
                with ui.nav_panel("Recent 25 records"):
                    @render.text
                    def header_text1():
                        return "{} Recent 25 'Closed' 311 Blocked Bike Lane Service Request from {} to {}".format(
                            input.ticker(), input.date_range()[0], input.date_range()[1]
                        )
                    @render.data_frame
                    def B_df():
                        p=['date','Time','incident_address','MinutesElapsed','resolution','resolution_description']
                        B= f_df()[p]
                        B.columns= ['Date','Time','Address','Response_Mins','Resolution','Description']
                        return render.DataTable(
                            B.head(25),width="1200px", height="500px",styles=df_styles1
                        )

        with ui.nav_menu("Sources"):
            with ui.nav_control():
                ui.a("Exploratory Analysis Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb", target="_blank")
                ui.a("311 Service Requests", href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/", target="_blank")
                ui.a("Github", href="https://github.com/sustainabu/OpenDataNYC/tree/main/311_BlockedBikeLane", target="_blank")

