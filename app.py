from dash import Dash, html, dcc, callback, Output, Input
from datetime import date
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import folium
from io import BytesIO
import base64

# Load data
df = pd.read_csv(
    "https://raw.githubusercontent.com/sustainabu/OpenDataNYC/refs/heads/main/311_BlockedBikeLane/dfc_out.csv"
)

# Data type adjustments
df["dateTime"] = pd.to_datetime(df["dateTime"]).dt.date
df["index_"] = df["index_"].astype(int)
df["MinutesElapsed"] = df["MinutesElapsed"].astype(float)

# Dropdown options
board_options = ["All"] + sorted(df["cboard_expand"].dropna().unique().astype(str))

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.title = "311 Blocked Bike Lane Dashboard"
update_date = date(2024, 12, 31)

# App layout
app.layout = html.Div([
    dcc.Tabs(id='tabs-nav', value='tab-1', children=[
        dcc.Tab(label='Discovery Mode', value='tab-1'),
        dcc.Tab(label='About', value='tab-2'),
    ]),
    html.Div(id='tabs-content'),
])

# Callback to render tab content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-nav', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dcc.Markdown("Each record is a 311 request for Blocked Bike Lane Violation. The dashboard displays NYPD responses, response-time, and call-density."),
            html.Div([
                dcc.Markdown("### Select Parameters")
            ], style={'padding': 10}),

            # Start and End Date Pickers
            html.Div([
                html.Div([
                    dcc.Markdown('''
                        **Start Date**
                        '''
                    ),
                    dcc.DatePickerSingle(
                        id='start-date',
                        min_date_allowed=date(2021, 1, 1),
                        max_date_allowed=update_date,
                        initial_visible_month=date(2023, 1, 1),
                        date=date(2023, 1, 1),
                        placeholder='Select Start Date'
                    ),
                ], style={'margin-right': '20px'}),

                html.Div([
                    html.H4("End Date"),
                    dcc.DatePickerSingle(
                        id='end-date',
                        min_date_allowed=date(2021, 1, 1),
                        max_date_allowed=update_date,
                        initial_visible_month=update_date,
                        date=update_date,
                        placeholder='Select End Date'
                    ),
                ], style={'margin-right': '20px'}),
            ], style={'display': 'flex', 'flex-direction': 'row', 'margin-bottom': '20px'}),

            # Dropdown for Board Selection
            html.Div([
                html.H4("Select Community Board"),
                dcc.Dropdown(board_options, value="All", id="dropdown", style={'margin-bottom': 20})
            ]),
            # Plot
            dcc.Graph(id="pie"),
            # Response Time Bar
            html.Div([
                dcc.RadioItems(
                    id="radio1",
                    options=[
                        {"label": "Statistics", "value": "stat"},
                        {"label": "Distribution", "value": "dist"},
                    ],
                    labelClassName="radio__labels",
                    inputClassName="radio__input",
                    value="stat",
                    className="radio__group",
                ),
                dcc.Graph(id="resolution_bar", config={'displayModeBar': False})
            ]),
            # Density Bar
            html.Div([
                dcc.RadioItems(
                    id="radio2",
                    options=[
                        {"label": "Distribution", "value": "dist"},
                        {"label": "Resolution", "value": "resolution"},
                        {"label": "Response Time", "value": "time"},
                    ],
                    labelClassName="radio__labels",
                    inputClassName="radio__input",
                    value="dist",
                    className="radio__group",
                ),
                dcc.Graph(id="density_bar", config={'displayModeBar': False})
            ]),
            # History Graph
            html.Div([
                dcc.RadioItems(
                    id="radio3",
                    options=[
                        {"label": "Requests", "value": "request"},
                        {"label": "InAction-Rate*", "value": "inaction"},
                    ],
                    labelClassName="radio__labels",
                    inputClassName="radio__input",
                    value="request",
                    className="radio__group",
                ),
                dcc.Graph(id="history", config={'displayModeBar': False})
            ]),
            # Density Bar
            html.Label("Select minimum map entries"),
            dcc.Slider(
                id="slider",
                min=1,
                max=10,
                step=1,
                marks={
                    1: "1",
                    3: "3",
                    5: "5",
                    7: "7",
                    10: "10",
                },
                value=3,
            ),
            html.Div([
                html.Div(id='folium')
            ]),
        ], style={'width': '80%', 'margin': 'auto'})

    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                dcc.Markdown("## About", style={'textAlign': 'center'}),
            ], style={'padding': 10}),

            html.Div([
                dcc.Markdown("""
                    ### Motivation:
                    Explore and analyze NYC blocked bike lane reports.
                """, style={'padding': 10}),
            ]),
        ], style={'width': '80%', 'margin': 'auto'})


# Callback to update plot based on input
@callback(
    Output("pie", "figure"),
    [Input('start-date', 'date'), 
     Input('end-date', 'date'), 
     Input("dropdown", "value")
     #,Input("radio", "value")
     ]
)
def update_graph(start_date, end_date, value):
    # Filter by board selection
    filtered_df = df[df["cboard_expand"] == value] if value != "All" else df

    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df["dateTime"] >= pd.to_datetime(start_date).date()) &
        (filtered_df["dateTime"] <= pd.to_datetime(end_date).date())
    ]

    # Filter by Radio Button
    #filtered_df = filtered_df.query('MinutesElapsed==MaxR_Mins and RepeatBin!="1"') if choice != "request" else filtered_df

    # Shortcut Renaming
    def valueT():
        if value != "All":
            return value.split(':')[0]
        else:
            return "All"

    # Group data for pie chart
    grouped_data = (
        filtered_df.groupby("resolution")["index_"]
        .sum()
        .reset_index()
        .rename(columns={"index_": "Count"})
    )

    # Create pie chart
    fig = px.pie(
        grouped_data,
        names="resolution",
        values="Count",
        title=f"Total 311 NYPD Service Resolutions for {valueT()}: {filtered_df['index_'].sum()}"
    )

    return fig

# Callback for Resolution Plots
@callback(
    Output("resolution_bar", "figure"),
    [Input('start-date', 'date'), 
     Input('end-date', 'date'), 
     Input("dropdown", "value"),
     Input("radio1", "value")
     ]
)
def bar_graph(start_date, end_date, value, choice):
    # Filter by board selection
    filtered_df = df[df["cboard_expand"] == value] if value != "All" else df

    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df["dateTime"] >= pd.to_datetime(start_date).date()) &
        (filtered_df["dateTime"] <= pd.to_datetime(end_date).date())
    ]

    # Shortcut Renaming
    def valueT():
        if value != "All":
            return value.split(':')[0]
        else:
            return "All"

    # Predefined resolution categories and elapsed minute bins    
    all_resolutions = ["Action", "Late", "No-Action", "Summon"]  # Add all possible resolution values here
    elapsed_bins = ["min0->5", "min5->30", "min30->60", "min60->360", "min360+"]  # Define all bins

    # Step 1: Aggregate Total, Median, and Mean
    cols_total = ["resolution", "index_"]
    cols_elapsed = ["resolution", "MinutesElapsed"]

    # Total count with predefined categories
    df_total = filtered_df[cols_total].groupby("resolution", observed=False).sum()
    df_total = df_total.reindex(all_resolutions, fill_value=0).reset_index()
    df_total.columns = ["resolution", "Total"]

    # Median of MinutesElapsed
    df_median = filtered_df[cols_elapsed].groupby("resolution", observed=False).median()
    df_median = df_median.reindex(all_resolutions, fill_value=0).reset_index()
    df_median = df_median.round(2)
    df_median.columns = ["resolution", "Median_Minutes"]

    # Mean of MinutesElapsed
    df_mean = filtered_df[cols_elapsed].groupby("resolution", observed=False).mean()
    df_mean = df_mean.reindex(all_resolutions, fill_value=0).reset_index()
    df_mean = df_mean.round(2)
    df_mean.columns = ["resolution", "Mean_Minutes"]

    # Merge Total, Median, and Mean
    merged_df = pd.merge(df_total, df_median, on="resolution", how="left")
    merged_df = pd.merge(merged_df, df_mean, on="resolution", how="left")

    # Step 2: Create Binned Count with all bins included
    bins_cols = ["resolution", "ElapsedMinuteBin", "index_"]

    # Group and pivot with predefined bins
    df_bins = filtered_df[bins_cols].groupby(["resolution", "ElapsedMinuteBin"]).sum().reset_index()
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
        round(filtered_df["MinutesElapsed"].median(), 2),
        round(filtered_df["MinutesElapsed"].mean(), 2),
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
            .round(1)  # Round to one decimal place
            #.apply(lambda x: f"{x:.1f}%")
        )
    
    fig1 = go.Figure(data=[
    go.Bar(name='Median', x=final_df['Police_resolution'], y=final_df['Median_Mins']),
    go.Bar(name='Mean', x=final_df['Police_resolution'], y=final_df['Mean_Mins'])
    ])
    fig1.update_layout(barmode='group',yaxis_title= 'Minutes',
                      title=f"NYPD Resolution Response Time for {valueT()}"
                      )
    
    ## horizontal graph
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=final_df["Police_resolution"],
        x=final_df['min0->5'],
        name='Min_0->5',
        orientation='h',
        #marker=dict(color='#19A0AA'),
        #text=male_percentages,
        #textfont_size=14,
        textposition='inside',  # Position the text inside the bars
    ))

    fig2.add_trace(go.Bar(
        y=final_df["Police_resolution"],
        x=final_df['min5->30'],
        name='Min_5->30',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    fig2.add_trace(go.Bar(
        y=final_df["Police_resolution"],
        x=final_df['min30->60'],
        name='Min_30->60',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))
    fig2.add_trace(go.Bar(
        y=final_df["Police_resolution"],
        x=final_df['min60->360'],
        name='Min_60->360',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))
    fig2.add_trace(go.Bar(
        y=final_df["Police_resolution"],
        x=final_df['min360+'],
        name='Min_360+',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    quarters = ['All_resolutions','Summon','Action','No-Action','Late']

    fig2.update_layout(
        xaxis=dict(ticksuffix='%'),
        yaxis=dict(categoryorder='array', categoryarray=quarters),
        barmode='stack',
        template='plotly_white',
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',
            y=-0.25,  # Position below the chart
            xanchor='center',
            x=0.5,  # Centered horizontally
            traceorder='normal'
        ),
        margin = dict(l=10, r=10, t=10, b=10),
    )
    
    #Select by Radio Button
    return fig2 if choice != "stat" else fig1

#Callback for Density Plots
@callback(
    Output("density_bar", "figure"),
    [Input('start-date', 'date'), 
     Input('end-date', 'date'), 
     Input("dropdown", "value"),
     Input("radio2", "value")
     ]
)
def density_graph(start_date, end_date, value, choice):
    # Filter by board selection
    filtered_df = df[df["cboard_expand"] == value] if value != "All" else df

    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df["dateTime"] >= pd.to_datetime(start_date).date()) &
        (filtered_df["dateTime"] <= pd.to_datetime(end_date).date())
    ]

    # Shortcut Renaming
    def valueT():
        if value != "All":
            return value.split(':')[0]
        else:
            return "All"

    # Predefined resolution categories and elapsed minute bins    
    dfc_unique= filtered_df.query('MinutesElapsed==MaxR_Mins')
    all_repeat = ["1", "2", "3", "4","5+"]  # Add all possible resolution values here
    resolution_bins = ["Action", "Late", "No-Action", "Summon"]  # Define all bins
    elapsed_bins = ["min0->5", "min5->30", "min30->60", "min60->360", "min360+"]  # Define all bins
    
    # Step 1: Aggregate Total, Median, and Mean
    cols_total = ["RepeatBin", "index_"]
    cols_elapsed = ["RepeatBin", "MinutesElapsed"]
    
    # Total count with predefined categories
    df_total = dfc_unique[cols_total].groupby("RepeatBin", observed=False).sum()
    df_total = df_total.reindex(all_repeat, fill_value=0).reset_index()
    df_total.columns = ["RepeatBin", "Total"]

    # Side Step to create 1 Fig 1
    # Group data for pie chart
    grouped_data = (
        dfc_unique.groupby("RepeatBin")["index_"]
        .sum()
        .reset_index()
        .rename(columns={"index_": "Count"})
    )
    # Create pie chart
    fig1 = px.pie(
        grouped_data,
        names="RepeatBin",
        values="Count",
        title=f"Total Call-Density Breakdown for {valueT()}: {dfc_unique['index_'].sum()}"
    )


    # Step 2: Create Binned Count with all bins included
    bins_cols = ["RepeatBin", "resolution", "index_"]
    
    # Group and pivot with predefined bins
    df_bins = dfc_unique[bins_cols].groupby(["RepeatBin", "resolution"]).sum().reset_index()
    df_bins["resolution"] = pd.Categorical(df_bins["resolution"], categories=resolution_bins, ordered=True)
    df_bins = df_bins.pivot_table(index="RepeatBin", columns="resolution", values="index_", fill_value=0).reset_index()
    
    # Ensure all bins are included
    df_bins = df_bins.reindex(columns=["RepeatBin"] + resolution_bins, fill_value=0)
    
    # Merge binned data with aggregated data
    result_df = pd.merge(df_total, df_bins, on="RepeatBin", how="left")
    result_df.columns = ["RepeatBin", "Total"] + resolution_bins
    
    # Step 2: Create Binned Count with all bins included
    bins_cols = ["RepeatBin", "ElapsedMinuteBin", "index_"]
    
    # Group and pivot with predefined bins
    df_bins = dfc_unique[bins_cols].groupby(["RepeatBin","ElapsedMinuteBin"]).sum().reset_index()
    df_bins["ElapsedMinuteBin"] = pd.Categorical(df_bins["ElapsedMinuteBin"], categories=elapsed_bins, ordered=True)
    df_bins = df_bins.pivot_table(index="RepeatBin", columns="ElapsedMinuteBin", values="index_", fill_value=0).reset_index()
    
    # Ensure all bins are included
    df_bins = df_bins.reindex(columns=["RepeatBin"] + elapsed_bins, fill_value=0)
    
    # Merge binned data with aggregated data
    result1_df = pd.merge(result_df, df_bins, on="RepeatBin", how="left")
    result1_df.columns = ["Call-Density", "Total","Action","Late","No-Action","Summon"] + elapsed_bins
    
    # Step 3: Add Citywide Totals
    city_data = [
        "All",
        result1_df["Total"].sum(),
        *[result1_df[bin].sum() for bin in resolution_bins],
        *[result1_df[bin].sum() for bin in elapsed_bins],
    ]
    
    citywide_df = pd.DataFrame([city_data], columns=result1_df.columns)
    
    # Combine aggregated data with citywide totals
    final_df = pd.concat([result1_df, citywide_df], ignore_index=True)

    
    # Step 4: Calculate percentages for binned columns
    final_bin=[ "Late", "No-Action","Action", "Summon","min0->5", "min5->30", "min30->60", "min60->360", "min360+"]
    
    for col in final_bin:
        final_df[col] = (
            final_df[col]
            .div(final_df["Total"])
            .fillna(0)
            .mul(100)
            .round(1)  # Round to one decimal place
        )
    
    ## horizontal graph
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['Late'],
        name='Late',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    fig2.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['No-Action'],
        name='No-Action',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    fig2.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['Action'],
        name='Action',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))
    fig2.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['Summon'],
        name='Summon',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    quarters = ['5+','4','3','2','1']

    fig2.update_layout(
        xaxis=dict(ticksuffix='%'),
        yaxis=dict(categoryorder='array', categoryarray=quarters),
        barmode='stack',
        template='plotly_white',
        yaxis_title= 'Call-Density',
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',
            y=-0.25,  # Position below the chart
            xanchor='center',
            x=0.5,  # Centered horizontally
            traceorder='normal'
        ),
        margin = dict(l=10, r=10, t=10, b=10),
    )

    ## horizontal graph
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['min0->5'],
        name='Min_0->5',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    fig3.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['min5->30'],
        name='Min_5->30',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    fig3.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['min30->60'],
        name='Min_30->60',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))
    fig3.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['min60->360'],
        name='Min_60->360',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))
    fig3.add_trace(go.Bar(
        y=final_df["Call-Density"],
        x=final_df['min360+'],
        name='Min_360+',
        orientation='h',
        textposition='inside',  # Position the text inside the bars
    ))

    quarters = ['5+','4','3','2','1']

    fig3.update_layout(
        xaxis=dict(ticksuffix='%'),
        yaxis=dict(categoryorder='array', categoryarray=quarters),
        barmode='stack',
        template='plotly_white',
        yaxis_title= 'Call-Density',
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',
            y=-0.25,  # Position below the chart
            xanchor='center',
            x=0.5,  # Centered horizontally
            traceorder='normal'
        ),
        margin = dict(l=10, r=10, t=10, b=10),
    )

    #Select by Radio Button
    if choice== "resolution":
        return fig2
    elif choice== "time":
        return fig3
    else:
        return fig1
    #return fig2 if choice != "time" else fig1

# 
#Callback for History Graph
@callback(
    Output("history", "figure"),
    [Input('start-date', 'date'), 
     Input('end-date', 'date'), 
     Input("dropdown", "value"),
     Input("radio3", "value")
     ]
)
def history_graph(start_date, end_date, value, choice):
    # Filter by board selection
    filtered_df = df[df["cboard_expand"] == value] if value != "All" else df

    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df["dateTime"] >= pd.to_datetime(start_date).date()) &
        (filtered_df["dateTime"] <= pd.to_datetime(end_date).date())
    ]

    # Shortcut Renaming
    def valueT():
        if value != "All":
            return value.split(':')[0]
        else:
            return "All"
        
    custom_palette = [ "#ff7f0e","#1f77b4", "#2ca02c", "#d62728", "#9467bd"]
    current_year = filtered_df.Year.max() 

    #filtered_df["Inaction"]= filtered_df["Late"] + filtered_df["No-Action"]
    
    #Inaction Df use Unique Values
    dfc_unique= filtered_df.query('MinutesElapsed==MaxR_Mins')
    p=['']
    # Get Total by Precinct
    p=['WeekBin', 'Year','Late', 'No-Action','index_']
    df1=dfc_unique[p].groupby(['WeekBin','Year']).sum().reset_index()
    df1.columns=['WeekBin','Year','Late','No-Action','total']
    df1['InAction_Rate']= round((df1['Late'] +df1['No-Action']) / df1['total'],2)

    # Choose plot data based on radio choice
    if choice == 'request':
        bg = filtered_df.groupby(['WeekBin', 'Year'])['index_'].sum().unstack()
        traces = []
        for year in bg.columns:
            linestyle = 'solid' if year == current_year else 'dash'
            traces.append(go.Scatter(
                x=bg.index, y=bg[year],
                mode='lines',
                name=str(year),
                line=dict(dash=linestyle, color=custom_palette[year % len(custom_palette)])
            ))

        title = f"311 NYPD Service Requests History for {valueT()}"
    else:
        traces = []
        for year in df1['Year'].unique():
            df_year = df1[df1['Year'] == year]
            linestyle = 'solid' if year == current_year else 'dash'
            traces.append(go.Scatter(
                x=df_year['WeekBin'], y=df_year['InAction_Rate'],
                mode='lines',
                name=str(year),
                line=dict(dash=linestyle, color=custom_palette[year % len(custom_palette)])
            ))

        title = f"311 NYPD Inaction Rate History for {valueT()}"

    # Create Plotly figure
    figure = go.Figure(data=traces)
    figure.update_layout(
        title=title,
        xaxis_title='WeekBin (0 = beginning of year)',
        yaxis_title='',
        legend_title='Year',
        template='plotly_white'
    )
    return figure 

#Callback for Folium Map
@callback(
    Output("folium", "srcDoc"),
    [Input('start-date', 'date'), 
     Input('end-date', 'date'), 
     Input("dropdown", "value"),
     Input("slider", "value")
     ]
)
def folium_map(start_date, end_date, value, slide):
    # Select only unique values
    df.dropna(subset=['precinct'], inplace=True)
    df.dropna(subset=['longitude'], inplace=True)
    dfc_unique= df.query('MinutesElapsed==MaxR_Mins')

    # Filter by board selection
    filtered_df = dfc_unique[dfc_unique["cboard_expand"] == value] if value != "All" else df

    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df["dateTime"] >= pd.to_datetime(start_date).date()) &
        (filtered_df["dateTime"] <= pd.to_datetime(end_date).date())
    ]

    # Calculate midpoint of latitude and longitude
    latitude_mid = (filtered_df.latitude.max() + filtered_df.latitude.min()) / 2
    longitude_mid = (filtered_df.longitude.max() + filtered_df.longitude.min()) / 2
    
    # Set default map location and zoom based on input
    if value == "All":
        zoom = 11.25
        map_location = [40.7128, -74.0060]  # Default NYC location
    else:
        zoom = 12.5
        map_location = [latitude_mid, longitude_mid]

    # Initialize folium map
    nyc_map = folium.Map(location=map_location, zoom_start=zoom, tiles="CartoDB positron", height='100%', control_scale=True)


    # Get Total by UAddress
    p=['incident_address','cboard', 'precinct','UAdd','longitude','latitude','index_']
    df1=filtered_df[p].groupby(['incident_address','cboard','precinct','UAdd','longitude','latitude']).sum().reset_index()
    df1.columns=['Address','cboard','precinct','UAdd','longitude','latitude','total']

    # Filter data based on input
    df1 = df1[df1['total'] > slide]

    # Get Elapsed Min Binned Count
    p2=['UAdd','ElapsedMinuteBin','index_']
    pv=filtered_df[p2].groupby(['UAdd','ElapsedMinuteBin']).sum().reset_index()
    pv2=pd.pivot_table(pv,index='UAdd', columns='ElapsedMinuteBin', values=['index_']).reset_index().fillna(0)

    #CHECK ORDER OF COLUMNS- Alphabetical
    pv2.columns=['UAdd',"min0->5", "min30->60", "min360+", "min5->30","min60->360"]  
    c1= pd.merge(df1, pv2, on='UAdd', how='right')

    # Get Resolution Count
    p2=['UAdd','resolution','index_']
    cv=filtered_df[p2].groupby(['UAdd','resolution']).sum().reset_index()
    cv2=pd.pivot_table(cv,index='UAdd', columns='resolution', values=['index_']).reset_index().fillna(0)

    #CHECK ORDER OF COLUMNS- Alphabetical
    cv2.columns=['UAdd','NYPD_Action','NYPD_Late','NYPD_No-Action','NYPD_Summon']
    B= pd.merge(c1, cv2, on='UAdd', how='right')

    # to get median
    p2=['UAdd','MinutesElapsed']
    C=filtered_df[p2].groupby(['UAdd']).median().reset_index()
    C.columns= ['UAdd','Median_Minutes']  
    C.Median_Minutes=round(C.Median_Minutes,2)
    D= pd.merge(B, C, on='UAdd', how='right') 
    # to get mean
    E=filtered_df[p2].groupby(['UAdd']).mean().reset_index()
    E.columns= ['UAdd','Mean_Minutes']  
    E.Mean_Minutes=round(E.Mean_Minutes,2)
    F= pd.merge(D, E, on='UAdd', how='right') 

    F['InAction_Rate']= round((F['NYPD_Late'] +F['NYPD_No-Action']) / F['total'],2)

   # B17= F.query('total>50').sort_values('Median_Minutes', ascending=False)


    def Resp(x):
        if x<=0.5:
            return "Low" #5 mins or less
        elif x>0.5 and x<=0.75:
            return "Medium"
        else:
            return "High" # greater than 360 mins
            
    F = F.copy()
    F['Inaction_rank'] = F['InAction_Rate'].apply(Resp)

    FA= F.query('Inaction_rank=="Low"')  
    for index, row in FA.iterrows(): 
        popup_text = "Address: {}<br> Total: {}<br> Inaction Rate: {}<br> Late#: {}<br> No-Action#: {}<br> Action#: {}<br> Summon#: {}"
        popup_text = popup_text.format(row['Address'],row['total'],row['InAction_Rate'], row["NYPD_Late"],row['NYPD_No-Action'], row['NYPD_Action'], row['NYPD_Summon'])
        folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                            radius=row['total'] / 15 + 3,
                            color="#007849",
                            popup=folium.Popup(popup_text, max_width=300),
                            fill=True).add_to(nyc_map)
    #
    FB=F.query('Inaction_rank=="Medium"')   
    for index, row in FB.iterrows(): 
        popup_text = "Address: {}<br> Total: {}<br> Inaction Rate: {}<br> Late#: {}<br> No-Action#: {}<br> Action#: {}<br> Summon#: {}"
        popup_text = popup_text.format(row['Address'],row['total'],row['InAction_Rate'], row["NYPD_Late"],row['NYPD_No-Action'], row['NYPD_Action'], row['NYPD_Summon'])
        folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                            radius=row['total'] / 15 + 3,
                            color="#FFB52E",
                            popup=folium.Popup(popup_text, max_width=300),
                            fill=True).add_to(nyc_map)
    # Greater than 25 count
    FC=F.query('Inaction_rank=="High"')
    for index, row in FC.iterrows(): 
        popup_text = "Address: {}<br> Total: {}<br> Inaction Rate: {}<br> Late#: {}<br> No-Action#: {}<br> Action#: {}<br> Summon#: {}"
        popup_text = popup_text.format(row['Address'],row['total'],row['InAction_Rate'], row["NYPD_Late"],row['NYPD_No-Action'], row['NYPD_Action'], row['NYPD_Summon'])
        folium.CircleMarker(location=(row["latitude"],row["longitude"]),
                            radius=row['total'] / 15 + 3,
                            color="#E32227",
                            popup=folium.Popup(popup_text, max_width=300),
                            fill=True).add_to(nyc_map)       
    return html.Iframe(
        srcDoc=nyc_map._repr_html_(),
        width='100%',
        height='600px',
        style={'border': 'none'}
    )

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
