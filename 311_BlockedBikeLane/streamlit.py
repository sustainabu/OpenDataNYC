import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Read Local Files
# Set the working directory and load data
df = pd.read_csv("dfc_out.csv")
with open("CommunityDistricts.geojson", "r") as f:
    cboard_geo = f.read()

# Data Preparation
df["dateTime"] = pd.to_datetime(df["dateTime"], format="%Y-%m-%d").dt.date
df["index_"] = df["index_"].astype(int)
df["MinutesElapsed"] = df["MinutesElapsed"].astype(float)

# Dropdown options for community boards
board_options = ["All"] + sorted(df["cboard_name"].dropna().astype(str).unique())

# Sidebar Input Controls
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", datetime(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime(2023, 12, 31))
selected_board = st.sidebar.selectbox("Select Community Board", board_options)
min_entries = st.sidebar.slider("Min. Entries for Map Display", min_value=1, max_value=10, value=3)

# Filter Data Based on Inputs
filtered_df = df[(df["dateTime"] >= start_date) & (df["dateTime"] <= end_date)]
if selected_board != "All":
    filtered_df = filtered_df[filtered_df["cboard_name"] == selected_board]

# Tabs for Navigation
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Interactive Maps", "About", "Sources"])

# 1. Dashboard Tab
with tab1:
    st.markdown("## Dashboard")
    st.markdown("[Exploratory Data Analysis Report](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb)")

    # Resolution Distribution Plot
    st.markdown("### Resolution Distribution")
    custom_palette = ["#ff7f0e", "#1f77b4", "#2ca02c", "#d62728", "#9467bd"]
    bg = filtered_df.groupby(["WeekBin", "Year"])["index_"].sum().unstack()
    plt.figure(figsize=(10, 6))
    plt.gca().set_prop_cycle(color=custom_palette)
    for year in bg.columns:
        linestyle = '-' if year == bg.columns.max() else '--'
        plt.plot(bg.index, bg[year], linestyle=linestyle, label=year)
    plt.xlabel("WeekBin (0=beginning of year)")
    plt.title(f"Resolution Distribution for {selected_board}")
    plt.legend(title="Year")
    st.pyplot(plt)

    # Summary Data Table
    st.markdown("### Summary Data Table")
    st.dataframe(filtered_df.head(25))

# 2. Interactive Maps Tab
with tab2:
    st.markdown("## Interactive Maps")

    # Generate Folium Map
    lat_mid = (filtered_df["latitude"].max() + filtered_df["latitude"].min()) / 2
    lon_mid = (filtered_df["longitude"].max() + filtered_df["longitude"].min()) / 2
    zoom = 11.25 if selected_board == "All" else 13

    map_obj = folium.Map(location=[lat_mid, lon_mid], zoom_start=zoom, tiles="CartoDB positron")
    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=row["index_"] / 15 + 3,
            popup=f"Address: {row['incident_address']}<br>Response Time: {row['MinutesElapsed']} mins",
            color="#007849" if row["MinutesElapsed"] <= 30 else ("#FFB52E" if row["MinutesElapsed"] <= 60 else "#E32227"),
            fill=True
        ).add_to(map_obj)
    
    st_folium(map_obj, width=700, height=500)

# 3. About Tab
with tab3:
    st.markdown("## About")
    st.markdown("This app provides insights into 311 blocked bike lane service requests.")

# 4. Sources Tab
with tab4:
    st.markdown("## Sources")
    st.markdown(
        "[311 Service Requests](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/)"
    )
    st.markdown(
        "[Exploratory Analysis Report](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb)"
    )

