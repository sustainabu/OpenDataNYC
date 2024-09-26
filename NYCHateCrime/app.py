

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
df = pd.read_csv(app_dir / "NYCHate_Abu.csv")
#Geofiles
with open(app_dir / "nyc-police-precincts.geojson", "r") as f:
    precinct_geo = json.load(f)
#CSS files
#ui.include_css(app_dir / "styles.css")

#2. Data Prep
#Prepare Time Data for filter
df.dateTime=pd.to_datetime(df['dateTime'], format='%Y-%m-%d')
df.dateTime = df.dateTime.dt.date
#GeOMAPPING
df.precinct=df.precinct.astype(str)  #needed for proper merge
state= geopandas.GeoDataFrame.from_features(precinct_geo, crs="EPSG:4326")
d=['geometry','precinct']
state= state[d] #base table for the coordinant map
#Input Variable Options
bias_options= ('All','Jewish','Non-Jewish', 'White', 'Transgender', 'Gay', 'Non-Gay','Black', 'Asian','Non-Asian','Lesbian', 'Muslim', 'Hispanic', 'Other Ethnicity', 'Catholic')

#4. Create Primary Reactive Table
@reactive.calc
def f_df():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker().startswith('Non-')== True: #anti
        mf=mf[(mf['bias'] != input.ticker()[4:])]
    elif input.ticker()=='All':
        mf=mf
    else:
        mf=mf[(mf['bias'] == input.ticker())]      
    return mf

# Secondary Reactive
@reactive.calc
def f_dfb():
    mf = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    return mf


#6 Standard Plots

# Display
ui.page_opts(title="NYC Hate Crimes Dashboard by Abu Nayeem 09/26/24 (View on Desktop)")
ui.nav_spacer()  # Push the navbar items to the right

with ui.sidebar():
    ui.input_date_range("date_range", "Select date range", start="2019-01-01",min="2019-01-01")
    ui.input_selectize("ticker", "Select biased group", choices=bias_options, selected="All")
    ui.input_numeric("obs", "Minimum Offense Count", 20, min=1, max=50) 


#3. Input Options 

with ui.nav_panel("Data"):
    ui.include_css(app_dir / "styles.css")
    ui.markdown(
    '''          
            The data is from 01/01/19 to 07/23/24. Click on `Links` for analysis report and other info
    '''
    )
    with ui.navset_pill(id="tab"):  
        with ui.nav_panel("Offense"):
            @render.plot
            def pieplot1():
                p2=['offense1','index_']
                gf=f_df()[p2].groupby(['offense1']).sum().reset_index()
                gf.columns=['offense1','Count']
                gf=gf[(gf['Count'] > input.obs())]
                Total = gf.Count.sum()
                fig=plt.pie(gf.Count, labels=gf.offense1, autopct='%1.0f%%')
                plt.title('NYC {} biased crimes by offense (total records {})'.format(input.ticker(),Total))
                plt.xlabel('')
                return fig

        with ui.nav_panel("Crime History"):
            @render.plot
            def lineplot1():
                p2=['month_bin','borough','index_']
                pv=f_df()[p2].groupby(['month_bin','borough']).sum().reset_index()
                pv1=pd.pivot_table(pv,index='month_bin', columns='borough', values=['index_']).reset_index().fillna(0) #replace null values
                #Renaming columns is important for indexing
                pv1.columns= ['month','Bronx','Brooklyn','Manhattan','Queens','Staten']
                # Graphing
                plt.title('NYC {} biased crimes by month)'.format(input.ticker()))
                col= ['Bronx','Brooklyn','Manhattan','Queens','Staten']
                bg=sns.lineplot(pv1[col])
                plt.xlabel("months")
                figure = bg.get_figure() 
                return figure

        with ui.nav_panel("Crime Map"):
            @render.ui
            def offense_map():
                NYC_map = folium.Map(location=[40.7128466, -73.9138168], zoom_start=10, tiles="OpenStreetMap")
                # Create a title element
                title_html = '''
                            <h3 align="center" style="font-size:20px"><b>Interactive Hate Crime Map by Police Precinct!! (Offense Count on hover)</b></h3>
                            '''
                title = folium.Element(title_html)

                # Add the title to the map
                NYC_map.get_root().html.add_child(title)

                # Get Total by Precinct
                p=['precinct','index_']
                df1=f_df()[p].groupby(['precinct']).sum().reset_index()
                df1.columns=['precinct','total']
                A=pd.merge(state, df1, on='precinct', how='right') 

                # Get Total by Offense1
                p2=['precinct','offense1','index_']
                pv=f_df()[p2].groupby(['precinct','offense1']).sum().reset_index()
                pv2=pd.pivot_table(pv,index='precinct', columns='offense1', values=['index_']).reset_index().fillna(0)
                pv2.columns= ['precinct','Aggravated Harassment 2','Assault(Minor)','Criminal Mischief','Felony Assault','Grand Larceny','Misc. Penal Law','Other','Robbery']
                geomerge= pd.merge(A, pv2, on='precinct', how='right') 

                colormap = branca.colormap.LinearColormap(
                vmin=geomerge["total"].quantile(0.0),
                vmax=geomerge["total"].quantile(1),
                colors=["white", "pink", "orange", "red", "darkred"],
                caption=("{} Bias NYC Hate Crimes Map by offense".format(input.ticker())),
                )

                tooltip = folium.GeoJsonTooltip(
                    fields=['precinct','total','Aggravated Harassment 2','Assault(Minor)','Criminal Mischief','Felony Assault','Grand Larceny','Misc. Penal Law','Other','Robbery'],
                    #aliases=["State:", "2015 Median Income(USD):", "Median % Change:"],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 1px solid black;
                        border-radius: 1px;
                        box-shadow: 1px;
                    """,
                    max_width=800,
                )

                g = folium.GeoJson(
                    geomerge,
                    style_function=lambda x: {
                        "fillColor": colormap(x["properties"]["total"])
                        if x["properties"]["total"] is not None
                        else "transparent",
                        "weight":1.5, #set thickness
                        "color": "black",
                        "fillOpacity": 0.6,
                    },
                    tooltip=tooltip,
                    #popup=popup,
                ).add_to(NYC_map)
                colormap.add_to(NYC_map)
                return NYC_map

        with ui.nav_panel("Bias Map"):
            @render.ui
            def bias_map():
                NYC_map = folium.Map(location=[40.7128466, -73.9138168], zoom_start=10, tiles="OpenStreetMap")
                # Create a title element
                title_html = '''
                            <h3 align="center" style="font-size:20px"><b>Interactive Hate Crime Map by Police Precinct!! (Bias Count on hover)</b></h3>
                            '''
                title = folium.Element(title_html)

                # Add the title to the map
                NYC_map.get_root().html.add_child(title)

                # Get Total by Precinct
                p=['precinct','index_']
                df1=f_dfb()[p].groupby(['precinct']).sum().reset_index()
                df1.columns=['precinct','total']
                A=pd.merge(state, df1, on='precinct', how='right') 

                # Get Total by Offense1
                p2=['precinct','bias','index_']
                pv=f_dfb()[p2].groupby(['precinct','bias']).sum().reset_index()
                pv2=pd.pivot_table(pv,index='precinct', columns='bias', values=['index_']).reset_index().fillna(0)
                pv2.columns= ['precinct','Asian','Black','Catholic','Gay','Hispanic','Jewish','Lesbian','Muslim','Other Ethnicity','Transgender','White']
                geomerge= pd.merge(A, pv2, on='precinct', how='right') 

                colormap = branca.colormap.LinearColormap(
                vmin=geomerge["total"].quantile(0.0),
                vmax=geomerge["total"].quantile(1),
                colors=["white", "pink", "orange", "red", "darkred"],
                caption=("NYC Hate Crimes Map by biased group".format(input.ticker())),
                )

                tooltip = folium.GeoJsonTooltip(
                    fields=['precinct','Asian','Black','Catholic','Gay','Hispanic','Jewish','Lesbian','Muslim','Other Ethnicity','Transgender','White'],
                    #aliases=["State:", "2015 Median Income(USD):", "Median % Change:"],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 1px solid black;
                        border-radius: 1px;
                        box-shadow: 1px;
                    """,
                    max_width=800,
                )

                g = folium.GeoJson(
                    geomerge,
                    style_function=lambda x: {
                        "fillColor": colormap(x["properties"]["total"])
                        if x["properties"]["total"] is not None
                        else "transparent",
                        "weight":1.5, #set thickness
                        "color": "black",
                        "fillOpacity": 0.6,
                    },
                    tooltip=tooltip,
                    #popup=popup,
                ).add_to(NYC_map)
                colormap.add_to(NYC_map)
                return NYC_map
             
        with ui.nav_menu("Links"):
            with ui.nav_control():
                ui.a("Exploratory Analysis Report", href="https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/NYCHateCrime/NYC%20Hate%20Crime%20ReportU.ipynb", target="_blank")
                ui.a("Data Source", href="https://data.cityofnewyork.us/Public-Safety/NYPD-Hate-Crimes/bqiq-cu78/about_data", target="_blank")
                ui.a("Github", href="https://github.com/sustainabu/OpenDataNYC/tree/main/NYCHateCrime", target="_blank")

with ui.nav_panel("About"):
    ui.markdown(
        '''
            ### ABOUT the Dataset
            * All the hate crimes are confirmed by the NYPD since 2019
            * Only '40%' led to an arrest. 
            * About '50%' of hate crimes were anti-Jewish
            * Some data entries were excluded you can learn more in [exploratory analysis report](https://nbviewer.org/github/sustainabu/OpenDataNYC/blob/main/NYCHateCrime/NYC%20Hate%20Crime%20ReportU.ipynb)
            ### ABOUT the Parameters 
            * Date-Range: impact all tables
            * Biased Group: impact all tables except Bias Map
                * The "Non" biased groups were selected due to high-frequency of base
            * Minimum offense count: impacts ONLY the Offense pie chart. 
                * It was included to reduce clutter, but not lose information
            ### ABOUT Me
            * I'm trained as an economist (MS Economics in UC) and self-learned programmer
            * I'm a community advocate and Jamaica, Queens resident
            * For other data projects, check out my [Github](https://github.com/sustainabu/OpenDataNYC)
            * I'm currently looking for job opportunities feel free to reach out to me (Abu: anayeem1@gmail.com)
        '''
        )


