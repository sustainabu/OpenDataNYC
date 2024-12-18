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
from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from htmltools import tags, HTML

#from shiny import App, ui, render,reactive

#1.Read local files 
app_dir = Path(__file__).parent #set environment local
#dataframe
df = pd.read_csv(app_dir / "dfc_out.csv")
#Geofiles
#with open(app_dir / "CommunityDistricts.geojson", "r") as f:
#s    cboard_geo = json.load(f)

#2. Data Prep
#Prepare Time Data for filter
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


# Display
ui.page_opts(title="311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem 12/08/24 (View on Desktop)")
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
                        plt.title("{} 311 Blocked Bike Lane Service Requests from {} to {}".format(
                            input.ticker(), input.date_range()[0], input.date_range()[1]))
                        plt.legend(title='Year')
                        figure = plt.gcf()
                        return figure
                    @render.text
                    def header_text():
                        return "NYPD Blocked Bike Lane Service Resolution & Reponse Times from"

                    @render.data_frame
                    def Summary_df():
                        # Style table with consistent dimensions
                        return render.DataTable(
                            final_df,
                            width="1500px",
                            height="500px",
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
                        plt.title("{} 311 Blocked Bike Lane Service Requests from {} to {}".format(
                            input.ticker(), input.date_range()[0], input.date_range()[1]))
                        plt.legend(title='Year')
                        figure = plt.gcf()
                        return figure

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
        with ui.nav_panel("Interactive Maps"):
            with ui.navset_card_underline():
                with ui.nav_panel("HotSpot"):
                    @render.ui
                    def responseTime_map():
                        # Find Midpoint of Latitude and Longitude of all points
                        LaMax=f_df().latitude.max()
                        LaMin=f_df().latitude.min()
                        Latitude=(LaMax+LaMin)/2
                        LoMax=f_df().longitude.max()
                        LoMin=f_df().longitude.min()
                        Longitude=(LoMax+LoMin)/2
                        
                        if input.ticker()=="All":
                            zo= 11.25
                            map_location = [40.7128, -74.0060]
                        else: 
                            zo=13  
                            map_location = [Latitude,Longitude]

                        # generate a new map
                        NYC_map = folium.Map(location=map_location, zoom_start=zo,tiles="CartoDB positron")               
                        
                        # Create a title element
                        title_html = '''
                                    <h3 align="center" style="font-size:20px"><b>HotSpot Map (Click and adjust parameters on the left) </b></h3>
                                    '''
                        title = folium.Element(title_html)

                        # Add the title to the map
                        NYC_map.get_root().html.add_child(title)

                        #Prepare Data
                        p=['incident_address','UAdd','cboard','longitude','latitude','index_',"min0->5","min5->30", "min30->60", "min60->360","min360+",'Miss','No-Action','Action','Summon']
                        df1=f_df()[p].groupby(['incident_address','UAdd','cboard','longitude','latitude']).sum().reset_index()
                        # to get median
                        p2=['UAdd','MinutesElapsed']
                        C=f_df()[p2].groupby(['UAdd']).median().reset_index()
                        C.columns= ['UAdd','MedianResponse_Minutes']   
                        C1= pd.merge(df1, C, on='UAdd', how='right') 
                        # to get meean
                        p2=['UAdd','MinutesElapsed']
                        C2=f_df()[p2].groupby(['UAdd']).mean().reset_index()
                        C2.columns= ['UAdd','MeanResponse_Minutes']   
                        D= pd.merge(C2, C1, on='UAdd', how='right') 
                        B17=D[(D['index_'] > input.obs())]

                        # Median less than 30
                        BA=B17.query('MedianResponse_Minutes<=30')
                        for index, row in BA.iterrows(): 
                            popup_text = "Address: {}<br> CBoard: {}<br> Total: {}<br> MedianResponseMin: {}<br> MeanResponseMin: {}<br> Min0->5: {}<br> Min5->30: {}<br> Min30->60: {}<br> Min60->360: {}<br> Min360+: {}<br> Response_Miss: {}<br> Response_No-Action: {}<br> Response_Action: {}<br> Response_Summons: {}"
                            popup_text = popup_text.format(row['incident_address'],row['cboard'] ,row['index_'],row['MedianResponse_Minutes'],row['MeanResponse_Minutes'], row["min0->5"],row["min5->30"], row["min30->60"], row["min60->360"],row["min360+"], row["Miss"],row['No-Action'], row['Action'], row['Summon'])
                            folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                                radius=row['index_']/15 +3,
                                                color="#007849",
                                                popup=popup_text,
                                                fill=True).add_to(NYC_map)
                        # Median between 30 and 60
                        BB=B17.query('MedianResponse_Minutes<=60 and MedianResponse_Minutes>30')   
                        for index, row in BB.iterrows(): 
                            popup_text = "Address: {}<br> CBoard: {}<br> Total: {}<br> MedianResponseMin: {}<br> MeanResponseMin: {}<br> Min0->5: {}<br> Min5->30: {}<br> Min30->60: {}<br> Min60->360: {}<br> Min360+: {}<br> Response_Miss: {}<br> Response_No-Action: {}<br> Response_Action: {}<br> Response_Summons: {}"
                            popup_text = popup_text.format(row['incident_address'],row['cboard'] ,row['index_'],row['MedianResponse_Minutes'],row['MeanResponse_Minutes'], row["min0->5"],row["min5->30"], row["min30->60"], row["min60->360"],row["min360+"], row["Miss"],row['No-Action'], row['Action'], row['Summon'])
                            folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                                radius=row['index_']/15 +3,
                                                color="#FFB52E",
                                                popup=popup_text,
                                                fill=True).add_to(NYC_map)
                        # Median above 60
                        BC=B17.query('MedianResponse_Minutes>60')
                        for index, row in BC.iterrows(): 
                            popup_text = "Address: {}<br> CBoard: {}<br> Total: {}<br> MedianResponseMin: {}<br> MeanResponseMin: {}<br> Min0->5: {}<br> Min5->30: {}<br> Min30->60: {}<br> Min60->360: {}<br> Min360+: {}<br> Response_Miss: {}<br> Response_No-Action: {}<br> Response_Action: {}<br> Response_Summons: {}"
                            popup_text = popup_text.format(row['incident_address'],row['cboard'] ,row['index_'],row['MedianResponse_Minutes'],row['MeanResponse_Minutes'], row["min0->5"],row["min5->30"], row["min30->60"], row["min60->360"],row["min360+"], row["Miss"],row['No-Action'], row['Action'], row['Summon'])
                            folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                                radius=row['index_']/15 +3,
                                                color="#E32227",
                                                popup=popup_text,
                                                fill=True).add_to(NYC_map)  

                        source_html = f"""
                                <div style="
                                position: fixed; 
                                bottom: 5px; 
                                left: 12%; 
                                transform: translateX(-50%);
                                z-index: 1000;
                                font-size: 18px; 
                                font-weight: bold;
                                background-color: #D3D3D3; 
                                padding: 5px 10px; 
                                border-radius: 5px; 
                                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);">
                                Source: <a href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/" target="_blank">311 Service Requests</a>
                                </div>
                                """
                        NYC_map.get_root().html.add_child(folium.Element(source_html))

                        legend_html = '''
                        <div style="position: fixed; 
                                    top: 50px; left: 50px; width: 220px; height: 120px; 
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
                        NYC_map.get_root().html.add_child(folium.Element(legend_html))
                        return NYC_map      
                 
                with ui.nav_panel("City-Wide NYPD Response HeatMap"):
                    ui.markdown(
                        '''
                        <div class="flourish-embed flourish-map" data-src="visualisation/20781545"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20781545/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                        '''
                        ) 

        with ui.nav_panel("About"):
            ui.markdown(
                ''' Blah
                '''
                )

        with ui.nav_menu("Sources"):
            with ui.nav_control():
                ui.a("Exploratory Analysis Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb", target="_blank")
