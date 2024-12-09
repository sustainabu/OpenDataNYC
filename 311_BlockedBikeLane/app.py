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
df.cboard=df.cboard.astype(int)  #needed for proper merge
state= geopandas.GeoDataFrame.from_features(cboard_geo, crs="EPSG:4326")
d=['geometry','boro_cd']
state= state[d]
state.columns=['geometry','cboard']
#Input Variable Options
board_options= ('All',"01 MANHATTAN", "02 MANHATTAN", "03 MANHATTAN", "04 MANHATTAN", "05 MANHATTAN", "06 MANHATTAN", "07 MANHATTAN", "08 MANHATTAN", "09 MANHATTAN", "10 MANHATTAN", "11 MANHATTAN", "12 MANHATTAN", "01 BRONX", "02 BRONX", "03 BRONX", "04 BRONX", "05 BRONX", "06 BRONX", "07 BRONX", "08 BRONX", "09 BRONX", "11 BRONX", "12 BRONX", "26 BRONX", "01 BROOKLYN", "02 BROOKLYN", "03 BROOKLYN", "04 BROOKLYN", "05 BROOKLYN", "06 BROOKLYN", "07 BROOKLYN", "08 BROOKLYN", "09 BROOKLYN", "10 BROOKLYN", "13 BROOKLYN", "14 BROOKLYN", "15 BROOKLYN", "18 BROOKLYN", "01 QUEENS", "02 QUEENS", "03 QUEENS", "04 QUEENS", "05 QUEENS", "06 QUEENS", "07 QUEENS", "11 QUEENS", "12 QUEENS", "14 QUEENS")

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker()=='All':
        mf=mf
    else:
        mf=mf[(mf['community_board'] == input.ticker())]      
    return mf

# Secondary Reactive
@reactive.calc
def f_dfb():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    return mf


# Display
ui.page_opts(title="311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem 12/08/24 (View on Desktop)")
ui.nav_spacer()  # Push the navbar items to the right


# Inputting Slideer
with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2023-01-01",min="2023-01-01")
    ui.input_selectize("ticker", "Select community board", choices=board_options, selected="All")
    ui.input_numeric("obs", "Minimum Service Request", 5, min=1, max=10) 
    ui.input_slider("val", "Slider label", min=0, max=100, value=50)


#3. Input Options 

with ui.nav_panel("Data"):
    ui.include_css(app_dir / "styles.css")
    ui.markdown(
    '''          
            The data is from 01/01/19 to 07/23/24. Click on `Links` for analysis report and other info
    '''
    )
    with ui.navset_pill(id="tab"):  
        with ui.nav_panel("Latest 25 records"):
            @render.data_frame
            def B_df():
                p=['dateTimeO','incident_address','MinutesElapsed','resolution','resolution_description']
                B= f_df()[p]
                B.columns= ['Date','Address','Response_Mins','Resolution','Description']
                return render.DataTable(
                    B.head(25),width="1000px", height="500px"
                )
        with ui.nav_panel("Resolution Dist"):
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

        with ui.nav_panel("RespTime Dist"):
            @render.plot
            def pieplot2():
                p2=['ElapsedMinuteBin','index_']
                gf=f_df()[p2].groupby(['ElapsedMinuteBin']).sum().reset_index()
                gf.columns=['ElapsedMinuteBin','Count']
                Median = round(f_df().MinutesElapsed.median(),2) 
                fig=plt.pie(gf.Count, labels=gf.ElapsedMinuteBin, autopct='%1.0f%%')
                plt.title('{} NYPD Response Time (Median: {} Mins)'.format(input.ticker(),Median))
                plt.xlabel('')
                return fig

        with ui.nav_panel("Service Map"):
            @render.ui
            def offense_map():
                data = [[101, [40.690187,-74.043877]],[102, [40.742496, -74.00915]],[103, [40.733965, -73.9887793]],[104, [40.7731795, -73.993936]],[105, [40.7642788,-73.97301]],[106, [40.7301590,-73.961284]],[107, [40.8011564, -73.959646]],
                        [108, [40.76904, -73.9418003]],[109, [40.8303719, -73.94014]],[110, [40.8359809, -73.9344523]],[111, [40.8008521, -73.92133752]],[112, [40.8359809, -73.9344523]],[164, [40.79687199, -73.9492332]],
                        [201, [40.8204754, -73.901292]],[202, [40.795808,-73.8968088]],[203, [40.837521, -73.880720]],[204, [40.844581,-73.902688]],[205, [40.8617,-73.89138]],[206, [40.84376077,-73.8718461]],[207, [40.8715757, -73.875188]],
                        [208, [40.911417, -73.896633]],[209, [40.835619, -73.8397948]],[210, [40.834667,-73.78833349]],[211, [40.86089,-73.828343]],[212, [40.883643,-73.793855]],[227, [40.869674,-73.87053738]],[226,[40.90294,-73.8678979]],[228,[40.86079,-73.773218]],
                        [301, [40.7141,73.924059]],[302, [40.70709,-73.96929]],[303, [40.68721,-73.918046]],[304, [40.682336,-73.896466]],[305, [40.69473, -73.8684]],[306, [40.6924,-74.001743]],[307, [40.661154, -73.98017]],
                        [308, [40.67983,-73.95829]],[309, [40.66449,-73.928722]],[310, [40.644039,-74.03231]],[311, [40.6088,-73.972994]],[312, [40.648257,-73.9713963]],[313, [40.5958,-73.98372]],[314, [40.655048,-73.9563]],[315, [40.58657,-73.918]],[316, [40.678898,-73.90349]],
                        [317,[40.65118,-73.907552]],[318,[40.586269,-73.915133]],[356, [40.584526,-73.9123679]],[355,[40.671622,-73.962571]],
                        [401, [40.79018,-73.90647]],[402, [40.75424,-73.8979]],[403, [40.76667,-73.86272]],[404, [40.739,-73.8475]],[405, [40.73429,-73.8877]],[406, [40.7154,-73.826]],[407, [40.76,-73.85249]],
                        [408, [40.726229,-73.7567]],[409, [40.704,-73.8170973]],[410, [40.650278,-73.857223]],[411, [40.778947,-73.7446137]],[412, [40.66632,-73.8016826]],[413,[40.637529,-73.7469432]],[414,[40.565287,-73.9097168]],
                        [480, [40.76667,-73.86272]],[481, [40.74343,-73.835915]],[482, [40.7114646,-73.8357]],[483, [40.637554,-73.7469397]],[484, [40.557676,-73.932222]],
                        [501, [40.641448,-74.159456]],[502, [40.57838,-74.073466]],[503, [40.536306,-74.1331958]],[595, [40.566422,-74.050508]]]
                
                # Create the pandas DataFrame 
                Loc = pd.DataFrame(data, columns = ['Community', 'Location'])  

                if input.ticker()=="All":
                    zo= 11.25
                    default_location = [40.7128, -74.0060]
                    map_location = default_location
                else: 
                    zo=13  
                    p=['cboard'] #iloc[0, 11]
                    A=f_df()[p]
                    map_location = Loc.loc[Loc['Community'] == A.iloc[0,0], 'Location'].iloc[0]


                # generate a new map
                NYC_map = folium.Map(location=[40.7128, -74.0060], zoom_start=zo,tiles="CartoDB positron")
                
                # Create a title element
                title_html = '''
                            <h3 align="center" style="font-size:20px"><b>Interactive Request Map (Click for Resolution)</b></h3>
                            '''
                title = folium.Element(title_html)

                # Add the title to the map
                NYC_map.get_root().html.add_child(title)


                Index =['incident_address','longitude','latitude', "index_",'Miss','No-Action','Action','Summon']
                B17=f_df()[Index].groupby(['incident_address','longitude','latitude']).sum().reset_index()
                # Less than 5 count
                BA=B17.query('index_<=5')
                for index, row in BA.iterrows(): 
                    popup_text = "Address: {}<br> Total: {}<br> Miss: {}<br> No-Action: {}<br> Action: {}<br> Summons: {}"
                    popup_text = popup_text.format(row['incident_address'],row['index_'], row["Miss"],row['No-Action'], row['Action'], row['Summon'])
                    folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                        radius=row['index_'] +2,
                                        color="#007849",
                                        popup=popup_text,
                                        fill=True).add_to(NYC_map)
                # Between 5 and 25 count
                BB=B17.query('index_<=25 and index_>5')   
                for index, row in BB.iterrows(): 
                    popup_text = "Address: {}<br> Total: {}<br> Miss: {}<br> No-Action: {}<br> Action: {}<br> Summons: {}"
                    popup_text = popup_text.format(row['incident_address'],row['index_'], row["Miss"],row['No-Action'], row['Action'], row['Summon'])
                    folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                        radius=row['index_']/5 +7,
                                        color="#E37222",
                                        popup=popup_text,
                                        fill=True).add_to(NYC_map)
                # Greater than 25 count
                BC=B17.query('index_>25')
                for index, row in BC.iterrows(): 
                    popup_text = "Address: {}<br> Total: {}<br> Miss: {}<br> No-Action: {}<br> Action: {}<br> Summons: {}"
                    popup_text = popup_text.format(row['incident_address'],row['index_'], row["Miss"],row['No-Action'], row['Action'], row['Summon'])
                    folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                        radius=row['index_']/15 +12,
                                        color="#800080",
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
 
        with ui.nav_panel("Response Time Map"):
            @render.ui
            def responseTime_map():
                data = [[101, [40.690187,-74.043877]],[102, [40.742496, -74.00915]],[103, [40.733965, -73.9887793]],[104, [40.7731795, -73.993936]],[105, [40.7642788,-73.97301]],[106, [40.7301590,-73.961284]],[107, [40.8011564, -73.959646]],
                        [108, [40.76904, -73.9418003]],[109, [40.8303719, -73.94014]],[110, [40.8359809, -73.9344523]],[111, [40.8008521, -73.92133752]],[112, [40.8359809, -73.9344523]],[164, [40.79687199, -73.9492332]],
                        [201, [40.8204754, -73.901292]],[202, [40.795808,-73.8968088]],[203, [40.837521, -73.880720]],[204, [40.844581,-73.902688]],[205, [40.8617,-73.89138]],[206, [40.84376077,-73.8718461]],[207, [40.8715757, -73.875188]],
                        [208, [40.911417, -73.896633]],[209, [40.835619, -73.8397948]],[210, [40.834667,-73.78833349]],[211, [40.86089,-73.828343]],[212, [40.883643,-73.793855]],[227, [40.869674,-73.87053738]],[226,[40.90294,-73.8678979]],[228,[40.86079,-73.773218]],
                        [301, [40.7141,73.924059]],[302, [40.70709,-73.96929]],[303, [40.68721,-73.918046]],[304, [40.682336,-73.896466]],[305, [40.69473, -73.8684]],[306, [40.6924,-74.001743]],[307, [40.661154, -73.98017]],
                        [308, [40.67983,-73.95829]],[309, [40.66449,-73.928722]],[310, [40.644039,-74.03231]],[311, [40.6088,-73.972994]],[312, [40.648257,-73.9713963]],[313, [40.5958,-73.98372]],[314, [40.655048,-73.9563]],[315, [40.58657,-73.918]],[316, [40.678898,-73.90349]],
                        [317,[40.65118,-73.907552]],[318,[40.586269,-73.915133]],[356, [40.584526,-73.9123679]],[355,[40.671622,-73.962571]],
                        [401, [40.79018,-73.90647]],[402, [40.75424,-73.8979]],[403, [40.76667,-73.86272]],[404, [40.739,-73.8475]],[405, [40.73429,-73.8877]],[406, [40.7154,-73.826]],[407, [40.76,-73.85249]],
                        [408, [40.726229,-73.7567]],[409, [40.704,-73.8170973]],[410, [40.650278,-73.857223]],[411, [40.778947,-73.7446137]],[412, [40.66632,-73.8016826]],[413,[40.637529,-73.7469432]],[414,[40.565287,-73.9097168]],
                        [480, [40.76667,-73.86272]],[481, [40.74343,-73.835915]],[482, [40.7114646,-73.8357]],[483, [40.637554,-73.7469397]],[484, [40.557676,-73.932222]],
                        [501, [40.641448,-74.159456]],[502, [40.57838,-74.073466]],[503, [40.536306,-74.1331958]],[595, [40.566422,-74.050508]]]
                
                # Create the pandas DataFrame 
                Loc = pd.DataFrame(data, columns = ['Community', 'Location'])  

                if input.ticker()=="All":
                    zo= 11.25
                    default_location = [40.7128, -74.0060]
                    map_location = default_location
                else: 
                    zo=13  
                    p=['cboard'] #iloc[0, 11]
                    A=f_df()[p]
                    map_location = Loc.loc[Loc['Community'] == A.iloc[0,0], 'Location'].iloc[0]


                # generate a new map
                NYC_map = folium.Map(location=[40.7128, -74.0060], zoom_start=zo,tiles="CartoDB positron")
                
                # Create a title element
                title_html = '''
                            <h3 align="center" style="font-size:20px"><b>Interactive NYPD Response Time Map (Click for Response Time)</b></h3>
                            '''
                title = folium.Element(title_html)

                # Add the title to the map
                NYC_map.get_root().html.add_child(title)

                #Prepare Data
                #Get Total count by address
                p=['incident_address','longitude','latitude','index_']
                df1=f_df()[p].groupby(['incident_address','longitude','latitude']).sum().reset_index()
                # Get Binned Count
                p2=['incident_address','ElapsedMinuteBin','index_']
                pv=f_df()[p2].groupby(['incident_address','ElapsedMinuteBin']).sum().reset_index()
                pv2=pd.pivot_table(pv,index='incident_address', columns='ElapsedMinuteBin', values=['index_']).reset_index().fillna(0)
                #CHECK ORDER OF COLUMNS
                pv2.columns=['incident_address',"min0->5", "min30->60", "min360+", "min5->30","min60->360"]  
                B= pd.merge(df1, pv2, on='incident_address', how='right') 
                # to get median
                p2=['incident_address','MinutesElapsed']
                C=f_df()[p2].groupby(['incident_address']).median().reset_index()
                C.columns= ['incident_address','MedianResponse_Minutes']   
                D= pd.merge(B, C, on='incident_address', how='right') 
                D.MedianResponse_Minutes=round(D.MedianResponse_Minutes,2)
                B17=D[(D['index_'] > input.obs())]

                # Median less than 30
                BA=B17.query('MedianResponse_Minutes<=30')
                for index, row in BA.iterrows(): 
                    popup_text = "Address: {}<br> Total: {}<br> MedianResponseMin: {}<br> Min0->5: {}<br> Min5->30: {}<br> Min30->60: {}<br> Min60->360: {}<br> Min360+: {}"
                    popup_text = popup_text.format(row['incident_address'],row['index_'],row['MedianResponse_Minutes'], row["min0->5"],row["min5->30"], row["min30->60"], row["min60->360"],row["min360+"])
                    folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                        radius=row['index_']/15 +3,
                                        color="#007849",
                                        popup=popup_text,
                                        fill=True).add_to(NYC_map)
                # Median between 30 and 60
                BB=B17.query('MedianResponse_Minutes<=60 and MedianResponse_Minutes>30')   
                for index, row in BB.iterrows(): 
                    popup_text = "Address: {}<br> Total: {}<br> MedianResponseMin: {}<br> Min0->5: {}<br> Min5->30: {}<br> Min30->60: {}<br> Min60->360: {}<br> Min360+: {}"
                    popup_text = popup_text.format(row['incident_address'],row['index_'], row['MedianResponse_Minutes'], row["min0->5"],row["min5->30"], row["min30->60"], row["min60->360"],row["min360+"])
                    folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                                        radius=row['index_']/15 +3,
                                        color="#FFB52E",
                                        popup=popup_text,
                                        fill=True).add_to(NYC_map)
                # Median above 60
                BC=B17.query('MedianResponse_Minutes>60')
                for index, row in BC.iterrows(): 
                    popup_text = "Address: {}<br> Total: {}<br> MedianResponseMin: {}<br> Min0->5: {}<br> Min5->30: {}<br> Min30->60: {}<br> Min60->360: {}<br> Min360+: {}"
                    popup_text = popup_text.format(row['incident_address'],row['index_'],row['MedianResponse_Minutes'], row["min0->5"],row["min5->30"], row["min30->60"], row["min60->360"],row["min360+"])
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
                 
        with ui.nav_panel("NYC Response Time Map [Fixed]"):
            ui.markdown(
                '''
                   <div class="flourish-embed flourish-map" data-src="visualisation/20685536"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/20685536/thumbnail" width="100%" alt="map visualization" /></noscript></div>
                '''
                )
        with ui.nav_menu("Links"):
            with ui.nav_control():
                ui.a("Exploratory Analysis Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/NYCHateCrime/NYC%20Hate%20Crime%20ReportU.ipynb", target="_blank")
                ui.a("Data Source", href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data/", target="_blank")
                ui.a("Github", href="https://github.com/sustainabu/OpenDataNYC/tree/main/311", target="_blank")


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
            * Learn More in the [data report]](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/NYCHateCrime/NYC%20Hate%20Crime%20ReportU.ipynb)
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