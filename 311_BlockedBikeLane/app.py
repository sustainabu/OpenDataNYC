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
#import geopandas
import plotly.express as px
from shinywidgets import render_plotly, render_widget
import matplotlib.pyplot as plt
from htmltools import tags, HTML
#from shinywidgets import output_widget 

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
 #   {
 #       "location": "body",
 #       "cols": [5],  # Target the 6th column (index 5)
 #       "style": {
 #           "width": "300px",  # Adjust the width as needed
 #           "white-space": "normal",  # Allow text wrapping if necessary
 #       },
 #   },
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
    ui.tags.script(
    """
    document.addEventListener('DOMContentLoaded', function() {
        const inputs = document.querySelectorAll('input[type="number"], input[type="text"]');
        inputs.forEach(input => {
            input.addEventListener('focus', function(e) {
                if (window.innerWidth <= 768) {  // Adjust width for mobile detection
                    e.target.blur();  // Remove focus to prevent the keyboard from popping up
                }
            });
        });
    });
    """)
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_select("ticker", "Select community board", choices=board_options, selected="All")
    ui.input_slider("obs", "Select Min. Entries for Map Display", min=1, max=8, value=3) 


#3. Input Options 

with ui.nav_panel("Data"):
    ui.include_css(app_dir / "styles.css")
    ui.markdown('''[Updated: 12/17/24]; For mobile: select parameters BELOW and access MAPS on menu''')
    with ui.navset_card_underline():
        with ui.nav_panel("Resolution Distribution"):
            @render.plot
            def pieplot1():
                p2=['resolution','index_']
                gf=f_df()[p2].groupby(['resolution']).sum().reset_index()
                gf.columns=['resolution','Count']
                Total = f_df().index_.sum() 
                fig=plt.pie(gf.Count, labels=gf.resolution, autopct='%1.0f%%')
                plt.title('{} NYPD Response Tot:{}'.format(input.ticker(),Total))
                plt.xlabel('')
                return fig

        with ui.nav_panel("Summary Table"):
            @render.text
            def header_text():
                return "{} NYPD Resolution & Reponse Times from {} to {}".format(
                    input.ticker(), input.date_range()[0], input.date_range()[1]
                )

            @render.data_frame
            def Summary_df():
                # Predefined resolution categories and elapsed minute bins
                all_resolutions = ["Action", "Miss", "No-Action", "Summon"]  # Add all possible resolution values here
                elapsed_bins = ["min0->5", "min5->30", "min30->60", "min60->360", "min360+"]  # Define all bins

                # Step 1: Aggregate Total, Median, and Mean
                cols_total = ["resolution", "index_"]
                cols_elapsed = ["resolution", "MinutesElapsed"]

                # Total count with predefined categories
                df_total = f_df()[cols_total].groupby("resolution", observed=False).sum()
                df_total = df_total.reindex(all_resolutions, fill_value=0).reset_index()
                df_total.columns = ["resolution", "Total"]

                # Median of MinutesElapsed
                df_median = f_df()[cols_elapsed].groupby("resolution", observed=False).median()
                df_median = df_median.reindex(all_resolutions, fill_value=0).reset_index()
                df_median = df_median.round(2)
                df_median.columns = ["resolution", "Median_Minutes"]

                # Mean of MinutesElapsed
                df_mean = f_df()[cols_elapsed].groupby("resolution", observed=False).mean()
                df_mean = df_mean.reindex(all_resolutions, fill_value=0).reset_index()
                df_mean = df_mean.round(2)
                df_mean.columns = ["resolution", "Mean_Minutes"]

                # Merge Total, Median, and Mean
                merged_df = pd.merge(df_total, df_median, on="resolution", how="left")
                merged_df = pd.merge(merged_df, df_mean, on="resolution", how="left")

                # Step 2: Create Binned Count with all bins included
                bins_cols = ["resolution", "ElapsedMinuteBin", "index_"]

                # Group and pivot with predefined bins
                df_bins = f_df()[bins_cols].groupby(["resolution", "ElapsedMinuteBin"]).sum().reset_index()
                df_bins["ElapsedMinuteBin"] = pd.Categorical(df_bins["ElapsedMinuteBin"], categories=elapsed_bins, ordered=True)
                df_bins = df_bins.pivot_table(index="resolution", columns="ElapsedMinuteBin", values="index_", fill_value=0).reset_index()

                # Ensure all bins are included
                df_bins = df_bins.reindex(columns=["resolution"] + elapsed_bins, fill_value=0)

                # Merge binned data with aggregated data
                result_df = pd.merge(merged_df, df_bins, on="resolution", how="left")
                result_df.columns = ["Police_resolution", "Total", "Median_Mins", "Mean_Mins"] + elapsed_bins
                new_order = [1,2,0,3]
                result_df = result_df.reindex(new_order)

                # Step 3: Add Citywide Totals
                city_data = [
                    "All_resolutions",
                    result_df["Total"].sum(),
                    round(f_df()["MinutesElapsed"].median(), 3),
                    round(f_df()["MinutesElapsed"].mean(), 3),
                    *[result_df[bin].sum() for bin in elapsed_bins],
                ]

                citywide_df = pd.DataFrame([city_data], columns=result_df.columns)

                # Combine aggregated data with citywide totals
                final_df = pd.concat([result_df, citywide_df], ignore_index=True)

                # Step 4: Calculate percentages for binned columns
                for col in elapsed_bins:
                    final_df[col] = (
                        final_df[col]
                        .div(final_df["Total"])
                        .fillna(0)
                        .mul(100)
                        .apply(lambda x: f"{x:.1f}%")
                    )

                # Style table with consistent dimensions
                return render.DataTable(
                    final_df,
                    height='100%',
                    styles=df_styles,
                    )
        with ui.nav_panel("History"):
            @render.plot
            def lineplot1():
                custom_palette = [ "#ff7f0e","#1f77b4", "#2ca02c", "#d62728", "#9467bd"]
                current_year = f_df().Year.max() 
                bg= f_df().groupby(['WeekBin','Year'])['index_'].sum().unstack()
                # Set the custom color cycle
                plt.figure(figsize=(10, 6))  # Optional: Adjust figure size
                plt.gca().set_prop_cycle(color=custom_palette)
                for year in bg.columns:
                    linestyle = '-' if year == current_year else '--'  # Solid for current year, dashed for previous years
                    plt.plot(
                        bg.index, bg[year], linestyle=linestyle, label=year
                    )   
                plt.xlabel('WeekBin (0=beginning of year)')
                plt.ylabel('')
                plt.title("{} 311 Requests by Week".format(input.ticker()))
                plt.legend(title='Year')
                figure = plt.gcf()
                return figure

        with ui.nav_panel("Recent 25 records"):
            @render.text
            def header_text1():
                return "{} Blocked Bike Lane Service Request from {} to {}".format(
                    input.ticker(), input.date_range()[0], input.date_range()[1]
                )
            @render.data_frame
            def B_df():
                p=['date','Time','incident_address','MinutesElapsed','resolution']
                B= f_df()[p]
                B.columns= ['Date','Time','Address','Response_Mins','Resolution']
                return render.DataTable(
                    B.head(25), height="500",styles=df_styles1,
                )
            
with ui.nav_panel("Interactive Maps"):
    with ui.navset_card_underline():
        with ui.nav_panel("City InAction Rate"):
            ui.markdown(
                '''
                <div class="flourish-embed flourish-map" data-src="visualisation/20876100"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20876100/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                '''
                ) 


        with ui.nav_panel("City Response Time"):
            ui.markdown(
                '''
                <div class="flourish-embed flourish-map" data-src="visualisation/20781545"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20781545/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                '''
                ) 
        with ui.nav_panel("Local HotSpot (Desktop)"):
            @render.text
            def header_text2():
                return "Click on hotspot: On left, adjust parameters"
            @render.ui
            def responseTime_map():
                """
                Render a Folium map with data points categorized by median response time.
                """

                # Calculate midpoint of latitude and longitude
                latitude_mid = (f_df().latitude.max() + f_df().latitude.min()) / 2
                longitude_mid = (f_df().longitude.max() + f_df().longitude.min()) / 2

                # Determine map location and zoom level
                if input.ticker() == "All":
                    zoom = 11.25
                    map_location = [40.7128, -74.0060]  # Default NYC location
                else:
                    zoom = 13
                    map_location = [latitude_mid, longitude_mid]

                # Initialize the Folium map
                nyc_map = folium.Map(
                    location=map_location,
                    zoom_start=zoom,
                    tiles="CartoDB positron",
                    control_scale=True,
                    height="100%"
                )

                # Prepare the data
                group_columns = [
                    'incident_address', 'UAdd', 'cboard', 'longitude', 'latitude', 'index_',
                    "min0->5", "min5->30", "min30->60", "min60->360", "min360+",
                    'Miss', 'No-Action', 'Action', 'Summon'
                ]
                df_grouped = f_df()[group_columns].groupby(
                    ['incident_address', 'UAdd', 'cboard', 'longitude', 'latitude']
                ).sum().reset_index()

                # Calculate median and mean response times
                median_response = f_df().groupby('UAdd')['MinutesElapsed'].median().reset_index()
                median_response.columns = ['UAdd', 'MedianResponse_Minutes']

                mean_response = f_df().groupby('UAdd')['MinutesElapsed'].mean().reset_index()
                mean_response.columns = ['UAdd', 'MeanResponse_Minutes']

                # Merge datasets
                merged_df = pd.merge(df_grouped, median_response, on='UAdd', how='right')
                merged_df = pd.merge(merged_df, mean_response, on='UAdd', how='right')

                # Round numerical values
                merged_df['MedianResponse_Minutes'] = merged_df['MedianResponse_Minutes'].round(2)
                merged_df['MeanResponse_Minutes'] = merged_df['MeanResponse_Minutes'].round(2)

                # Filter data based on the observation threshold
                filtered_df = merged_df[merged_df['index_'] > input.obs()]

                # Define marker categories
                categories = [
                    ("MedianResponse_Minutes <= 30", "#007849"),  # Green
                    ("30 < MedianResponse_Minutes <= 60", "#FFB52E"),  # Orange
                    ("MedianResponse_Minutes > 60", "#E32227")  # Red
                ]

                # Add markers to the map
                for query, color in categories:
                    category_df = filtered_df.query(query)
                    for _, row in category_df.iterrows():
                        popup_text = (
                            f"Address: {row['incident_address']}<br>"
                            f"CBoard: {row['cboard']}<br>"
                            f"Total: {row['index_']}<br>"
                            f"MedianMin: {row['MedianResponse_Minutes']}<br>"
                            f"MeanMin: {row['MeanResponse_Minutes']}<br>"
                            f"Min0->5: {row['min0->5']}<br>"
                            f"Min5->30: {row['min5->30']}<br>"
                            f"Min30->60: {row['min30->60']}<br>"
                            f"Min60->360: {row['min60->360']}<br>"
                            f"Min360+: {row['min360+']}<br>"
                            f"Miss#: {row['Miss']}<br>"
                            f"No-Action#: {row['No-Action']}<br>"
                            f"Action#: {row['Action']}<br>"
                            f"Summon#: {row['Summon']}"
                        )
                        folium.CircleMarker(
                            location=(row["latitude"], row["longitude"]),
                            radius=row['index_'] / 15 + 3,
                            color=color,
                            popup=popup_text,
                            fill=True
                        ).add_to(nyc_map)

                # Add legend to the map
                legend_html = '''
                <div style="position: fixed; 
                            top: 20px; left: 50px; width: 180px; height: 100px; 
                            background-color: white; z-index:9999; font-size:14px;
                            border:2px solid grey; border-radius:5px; padding: 10px;">
                    <strong>Median Response Time</strong>
                    <br>
                    <i style="background:#007849; width:10px; height:10px; float:left; margin-right:5px;"></i> 0-30 Minutes
                    <br>
                    <i style="background:#FFB52E; width:10px; height:10px; float:left; margin-right:5px;"></i> 30-60 Minutes
                    <br>
                    <i style="background:#E32227; width:10px; height:10px; float:left; margin-right:5px;"></i> 60+ Minutes
                </div>
                '''
                nyc_map.get_root().html.add_child(folium.Element(legend_html))

                return nyc_map

        with ui.nav_panel("Local HotSpot (Phone)"):
            @render.text
            def header_text3():
                return "Clickable; Adjust parameters at bottom"
            @render.ui
            def responseTime_map2():
                # Calculate midpoint of latitude and longitude
                latitude_mid = (f_df().latitude.max() + f_df().latitude.min()) / 2
                longitude_mid = (f_df().longitude.max() + f_df().longitude.min()) / 2
                
                # Set default map location and zoom based on input
                if input.ticker() == "All":
                    zoom = 11.25
                    map_location = [40.7128, -74.0060]  # Default NYC location
                else:
                    zoom = 13
                    map_location = [latitude_mid, longitude_mid]

                # Initialize folium map
                nyc_map = folium.Map(location=map_location, zoom_start=zoom, tiles="CartoDB positron", height='100%', control_scale=True)

                # Prepare Data
                group_columns = [
                    'incident_address', 'UAdd', 'cboard', 'longitude', 'latitude', 'index_', 
                    "min0->5", "min5->30", "min30->60", "min60->360", "min360+", 
                    'Miss', 'No-Action', 'Action', 'Summon'
                ]
                df_grouped = f_df()[group_columns].groupby(
                    ['incident_address', 'UAdd', 'cboard', 'longitude', 'latitude']
                ).sum().reset_index()

                # Calculate median and mean response times
                median_response = f_df().groupby('UAdd')['MinutesElapsed'].median().reset_index()
                median_response.columns = ['UAdd', 'MedianResponse_Minutes']

                mean_response = f_df().groupby('UAdd')['MinutesElapsed'].mean().reset_index()
                mean_response.columns = ['UAdd', 'MeanResponse_Minutes']

                merged_df = pd.merge(df_grouped, median_response, on='UAdd', how='right')
                merged_df = pd.merge(merged_df, mean_response, on='UAdd', how='right')

                # Round values
                merged_df['MedianResponse_Minutes'] = merged_df['MedianResponse_Minutes'].round(2)
                merged_df['MeanResponse_Minutes'] = merged_df['MeanResponse_Minutes'].round(2)

                # Filter data based on input
                filtered_df = merged_df[merged_df['index_'] > input.obs()]

                # Define marker categories
                categories = [
                    ("MedianResponse_Minutes <= 30", "#007849"),  # Green
                    ("MedianResponse_Minutes <= 60 and MedianResponse_Minutes > 30", "#FFB52E"),  # Orange
                    ("MedianResponse_Minutes > 60", "#E32227")  # Red
                ]

                # Add markers to the map
                for query, color in categories:
                    category_df = filtered_df.query(query)
                    for _, row in category_df.iterrows():
                        popup_text = (
                            f"Address: {row['incident_address']}<br>"
                            f"Total: {row['index_']}<br>"
                            f"MedianMin: {row['MedianResponse_Minutes']}<br>"
                            f"MeanMin: {row['MeanResponse_Minutes']}<br>"
                            f"Miss#: {row['Miss']}<br>"
                            f"No-Action#: {row['No-Action']}<br>"
                            f"Action#: {row['Action']}<br>"
                            f"Summon#: {row['Summon']}"
                        )
                        folium.CircleMarker(
                            location=(row["latitude"], row["longitude"]),
                            radius=row['index_'] / 15 + 3,
                            color=color,
                            popup=popup_text,
                            fill=True
                        ).add_to(nyc_map)

                return nyc_map


        
with ui.nav_menu("Links"):
    with ui.nav_control():
        ui.a("Exploratory Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb", target="_blank")
        ui.a("AI Traffic Study", href="https://nyc.streetsblog.org/2024/10/29/study-exposes-nypds-systemic-failure-to-enforce-safety-related-parking-violations", target="_blank")
        ui.a("311 Service Data", href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/", target="_blank")
        ui.a("Github", href="https://github.com/sustainabu/OpenDataNYC/tree/main/311_BlockedBikeLane", target="_blank")



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
            * My name is Abu Nayeem. I'm a community advocate and Jamaica, Queens resident
            * I'm trained as an economist (MS Economics in UC Berkeley) and self-learned programmer
            * For other data projects, check out my [Github](https://github.com/sustainabu/OpenDataNYC)
            * I'm currently looking for job opportunities feel free to reach out to me (Abu: anayeem1@gmail.com)
        '''
        )


