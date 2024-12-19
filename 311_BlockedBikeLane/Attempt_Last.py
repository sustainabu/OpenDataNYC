import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
import folium
from shiny import reactive, App, Inputs, Outputs, Session, render, ui
import plotly.express as px
from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from htmltools import tags, HTML


#from shiny import App, ui, render,reactive

#1.Read local files 
app_dir = Path(__file__).parent #set environment local
#dataframe
df = pd.read_csv(app_dir / "dfc_out.csv")

df.dateTime=pd.to_datetime(df['dateTime'], format='%Y-%m-%d')
df.dateTime = df.dateTime.dt.date
df.index_=df.index_.astype(int)
df.MinutesElapsed=df.MinutesElapsed.astype(float)

board_options = ["All"] + sorted(df['cboard_name'].dropna().astype(str).unique())


#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker() != "All":
        mf = mf[mf["cboard_name"] == input.ticker()]
    return mf



app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider("n", "N", min=0, max=100, value=20),
            ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01"),
            ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All"),
            ui.input_numeric("obs", "Select Min. Entries for Map Display", 3, min=1, max=10), 
        ),
        ui.markdown(
        '''          
                [Date Updated: 12/17/24]; View Exploratory Data Analysis
        '''
        ), 
        #ui.include_css(app_dir / "styles.css"),
        ui.navset_tab(
            ui.nav_panel("Data", ui.output_data_frame("summary_df")),
            ui.nav_panel("Plot", ui.output_plot("plot")),
            ui.nav_panel("Pie", ui.output_plot("pieplot1")),
        ),   
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame()
    def summary_df() -> object:
        return render.DataTable(
            f_df().head(20),
        )
        
    @render.plot(alt="A histogram")
    def plot() -> object:
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig
    
    @render.plot
    def pieplot1()-> object:
        # Data Preparation for Pie Chart
        gf = (
            f_df()[["resolution", "index_"]]
            .groupby("resolution")
            .sum()
            .reset_index()
        )
        gf.columns = ["resolution", "Count"]
        total_records = f_df()["index_"].sum()

        # Create Pie Chart
        fig, ax = plt.subplots()
        ax.pie(gf["Count"], labels=gf["resolution"], autopct='%1.0f%%')
        ax.set_title(
            f'{input.ticker()} NYPD Blocked Bike Lane Resolution ({total_records} records)'
        )
        return fig
    


app = App(app_ui, server)

