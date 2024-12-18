import pandas as pd
from pathlib import Path
import json
import matplotlib.pyplot as plt
from shiny.express import input, render, ui, App

# 1. Read local files
App_dir = Path(__file__).parent  # Set environment to local directory

# DataFrame
df = pd.read_csv(App_dir / "dfc_out.csv")
df["dateTime"] = pd.to_datetime(df["dateTime"], format='%Y-%m-%d').dt.date
df["index_"] = df["index_"].astype(int)
df["MinutesElapsed"] = df["MinutesElapsed"].astype(float)

# GeoJSON file
with open(App_dir / "CommunityDistricts.geojson", "r") as f:
    cboard_geo = json.load(f)

# Define community board options
board_options = [
    "All",
    *[f"{str(i).zfill(2)} {borough}" for borough in ["MANHATTAN", "BRONX", "BROOKLYN", "QUEENS", "STATEN ISLAND"] for i in range(1, 13)],
    "26 BRONX",
    "16 BROOKLYN", "17 BROOKLYN", "18 BROOKLYN",
    "13 BROOKLYN", "14 BROOKLYN", "15 BROOKLYN",
    "13 QUEENS", "14 QUEENS"
]

# Shiny Express UI
ui.page_opts(title="Model Scoring Dashboard", fillable=True)

with ui.sidebar():
    input.date_range("date_range", "Select date range", start="2023-01-01", min="2023-01-01")
    input.selectize("ticker", "Select community board", choices=board_options, selected="All")

with ui.navset():
    with ui.nav("Data"):
        with ui.accordion("Summary Data"):
            ui.dataframe("Summary_df")
        with ui.accordion("Latest 25 Records"):
            ui.dataframe("Top25_df")
    with ui.nav("History"):
        ui.output_plot("lineplot1")
    with ui.nav("About"):
        ui.markdown("### Purpose\nThis dashboard helps explore 311 service request data.")

# Shiny Express Server Logic
@render.dataframe
def Top25_df():
    filtered_df = df[
        (df["dateTime"] >= input.date_range()[0]) & 
        (df["dateTime"] <= input.date_range()[1])
    ]
    if input.ticker() != "All":
        filtered_df = filtered_df[filtered_df["community_board"] == input.ticker()]

    columns = ["date", "Time", "incident_address", "MinutesElapsed", "resolution", "resolution_description"]
    filtered_df = filtered_df[columns]
    filtered_df.columns = ["Date", "Time", "Address", "Response Mins", "Resolution", "Description"]
    return filtered_df.head(25)

@render.dataframe
def Summary_df():
    filtered_df = df[
        (df["dateTime"] >= input.date_range()[0]) & 
        (df["dateTime"] <= input.date_range()[1])
    ]
    if input.ticker() != "All":
        filtered_df = filtered_df[filtered_df["community_board"] == input.ticker()]

    summary = filtered_df.groupby("resolution").agg(
        Total=("index_", "sum"),
        Median_Minutes=("MinutesElapsed", "median"),
        Mean_Minutes=("MinutesElapsed", "mean")
    ).reset_index()
    return summary.round(2)

@render.plot
def lineplot1():
    filtered_df = df[
        (df["dateTime"] >= input.date_range()[0]) & 
        (df["dateTime"] <= input.date_range()[1])
    ]
    if input.ticker() != "All":
        filtered_df = filtered_df[filtered_df["community_board"] == input.ticker()]

    bg = filtered_df.groupby(['WeekBin', 'Year'])['index_'].sum().unstack()
    current_year = bg.columns.max()

    plt.figure(figsize=(10, 6))
    for year in bg.columns:
        linestyle = '-' if year == current_year else '--'
        plt.plot(bg.index, bg[year], linestyle=linestyle, label=year)

    plt.xlabel('WeekBin (0=beginning of year)')
    plt.ylabel('Blocked Bike Lane Requests')
    plt.title(f"{input.ticker()} Blocked Bike Lane Requests")
    plt.legend(title='Year')
    return plt.gcf()

# Launch the Shiny Express App
#App()
