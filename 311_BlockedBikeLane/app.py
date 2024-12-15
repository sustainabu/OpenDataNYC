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
with open(app_dir / "CommunityDistricts.geojson", "r") as f:
    cboard_geo = json.load(f)

#2. Data Prep
#Prepare Time Data for filter
df.dateTime=pd.to_datetime(df['dateTime'], format='%Y-%m-%d')
df.dateTime = df.dateTime.dt.date
df.index_=df.index_.astype(int)
df.MinutesElapsed=df.MinutesElapsed.astype(float)
#GeOMAPPING
#df.cboard=df.cboard.astype(int)  #needed for proper merge
#state= geopandas.GeoDataFrame.from_features(cboard_geo, crs="EPSG:4326")
#d=['geometry','boro_cd']
#state= state[d]
#state.columns=['geometry','cboard']
#Input Variable Options
board_options= ('All',"01 MANHATTAN", "02 MANHATTAN", "03 MANHATTAN", "04 MANHATTAN", "05 MANHATTAN", "06 MANHATTAN", "07 MANHATTAN", "08 MANHATTAN", "09 MANHATTAN", "10 MANHATTAN", "11 MANHATTAN", "12 MANHATTAN", "01 BRONX", "02 BRONX", "03 BRONX", "04 BRONX", "05 BRONX", "06 BRONX", "07 BRONX", "08 BRONX", "09 BRONX","10 BRONX", "11 BRONX", "12 BRONX", "26 BRONX", "01 BROOKLYN", "02 BROOKLYN", "03 BROOKLYN", "04 BROOKLYN", "05 BROOKLYN", "06 BROOKLYN", "07 BROOKLYN", "08 BROOKLYN", "09 BROOKLYN", "10 BROOKLYN","11 BROOKLYN","12 BROOKLYN", "13 BROOKLYN", "14 BROOKLYN", "15 BROOKLYN","16 BROOKLYN","17 BROOKLYN", "18 BROOKLYN", "01 QUEENS", "02 QUEENS", "03 QUEENS", "04 QUEENS", "05 QUEENS", "06 QUEENS", "07 QUEENS","08 QUEENS","09 QUEENS","10 QUEENS", "11 QUEENS", "12 QUEENS","13 QUEENS", "14 QUEENS","01 STATEN ISLAND","02 STATEN ISLAND","03 STATEN ISLAND")

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
]

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker()=='All':
        mf=mf
    else:
        mf=mf[(mf['community_board'] == input.ticker())]      
    return mf

# Display
ui.page_opts(title="311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem 12/08/24 (View on Desktop)")
ui.nav_spacer()  # Push the navbar items to the right


# Inputting Slideer
with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All")
    ui.input_numeric("obs", "Select Min. Entries for Map", 5, min=1, max=10) 


#3. Input Options 

with ui.nav_panel("Data"):
    ui.include_css(app_dir / "styles.css")
    ui.markdown(
    '''          
            [Updated: 12/6/24] Note: Maps are interactive and click on `Links` for Exploratory Analysis
    '''
    )
    with ui.navset_pill(id="tab"):  
        with ui.nav_panel("Latest 25 records"):
            @render.data_frame
            def B_df():
                p=['date','Time','incident_address','MinutesElapsed','resolution','resolution_description']
                B= f_df()[p]
                B.columns= ['Date','Time','Address','Response_Mins','Resolution','Description']
                return render.DataTable(
                    B.head(25),width="1000px", height="500px",styles=df_styles1
                )
#        with ui.nav_panel("Resolution Dist"):
#            @render.plot
#            def pieplot1():
#                p2=['resolution','index_']
#                gf=f_df()[p2].groupby(['resolution']).sum().reset_index()
#                gf.columns=['resolution','Count']
#                Total = f_df().index_.sum() 
#                fig=plt.pie(gf.Count, labels=gf.resolution, autopct='%1.0f%%')
#                plt.title('{} NYPD Service Request Resolutions ({} records)'.format(input.ticker(),Total))
#                plt.xlabel('')
#                return fig

#        with ui.nav_panel("RespTime Dist"):
#            @render.plot
#            def pieplot2():
#                p2=['ElapsedMinuteBin','index_']
#                gf=f_df()[p2].groupby(['ElapsedMinuteBin']).sum().reset_index()
#                gf.columns=['ElapsedMinuteBin','Count']
#                Median = round(f_df().MinutesElapsed.median(),2) 
#                fig=plt.pie(gf.Count, labels=gf.ElapsedMinuteBin, autopct='%1.0f%%')
#                plt.title('{} NYPD Response Time (Median: {} Mins)'.format(input.ticker(),Median))
#                plt.xlabel('')
#                return fig

        with ui.nav_panel("Summary Table"):
            @render.data_frame
            def Sum_df():
                p=['resolution','index_']
                df1=f_df()[p].groupby(['resolution']).sum().reset_index() #Total
                df1.columns=['resolution','Total']
                p1=['resolution','MinutesElapsed']
                df2=round(f_df()[p1].groupby(['resolution']).median().reset_index(),2) #Median
                df2.columns=['resolution','Median_Minutes']
                C1= pd.merge(df1, df2, on='resolution', how='right') #Merge
                df3=round(f_df()[p1].groupby(['resolution']).mean().reset_index(),2) # Mean
                df3.columns=['resolution','Mean_Minutes']
                C2= pd.merge(C1, df3, on='resolution', how='right') #Merge

                # Get Binned Count
                p2=['resolution','ElapsedMinuteBin','index_']
                pv=f_df()[p2].groupby(['resolution','ElapsedMinuteBin']).sum().reset_index()
                pv2=pd.pivot_table(pv,index='resolution', columns='ElapsedMinuteBin', values=['index_']).reset_index().fillna(0)
                pv2.columns=['resolution',"min0->5", "min30->60", "min360+", "min5->30","min60->360"] 
                o1= ['resolution',"min0->5", "min5->30","min30->60", "min60->360", "min360+"] 
                A= pd.merge(C2, pv2[o1], on='resolution', how='right')
                A.columns=["Police_resolution", "Total", "Median_Mins", "Mean_Mins", "min0->5", "min5->30", "min30->60", "min60->360", "min360+"]

                new_order = [1, 2, 0,3] # New order of indices
                A = A.reindex(new_order) 

                # Assuming citydata is a single row of data
                citydata = [
                    "All_resolutions", 
                    A.Total.sum(), 
                    round(f_df()['MinutesElapsed'].median(),3), 
                    round(f_df()['MinutesElapsed'].mean(),3), 
                    A["min0->5"].sum(), 
                    A["min5->30"].sum(), 
                    A["min30->60"].sum(), 
                    A["min60->360"].sum(), 
                    A["min360+"].sum()
                ]

                # Creating a DataFrame for a single row
                All = pd.DataFrame([citydata], columns=["Police_resolution", "Total", "Median_Mins", "Mean_Mins", "min0->5", "min5->30", "min30->60", "min60->360", "min360+"])
                #Merge Everything
                B = pd.concat([A, All], ignore_index=True)

                #Set Percentages
                columns_to_convert = ["min0->5", "min5->30", "min30->60", "min60->360", "min360+"]
                for col in columns_to_convert:
                    B[col] = B[col].div(B["Total"]).fillna(0).mul(100).apply(lambda x: f"{x:.1f}%")

                B.style.set_table_styles([{'selector': '', 'props': [('border', '1px solid black')]}]).to_html()
                return render.DataTable(
                    #B.style.set_table_attributes('class="styled-table"')
                    B,width="1000px", height="500px", 
                    summary="Show entries",styles=df_styles
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
                plt.title("{} Blocked Bike Lane Requests".format(input.ticker()))
                plt.legend(title='Year')
                figure = plt.gcf()
                return figure
 
        with ui.nav_panel("ResponseTime Map "):
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
                            <h3 align="center" style="font-size:20px"><b>Interactive NYPD Median Response Time Map </b></h3>
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
                return NYC_map      
                 
        with ui.nav_panel("NYC Response Time HeatMap"):
            ui.markdown(
                '''
                   <div class="flourish-embed flourish-map" data-src="visualisation/20781545"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20781545/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                '''
                )
        with ui.nav_menu("Links"):
            with ui.nav_control():
                ui.a("Exploratory Analysis Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb", target="_blank")
                ui.a("Data Source", href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/", target="_blank")
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
            * Learn More in the [data report]](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/311_BlockedBikeLane/BlockBikeLane%20Report.ipynb)
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