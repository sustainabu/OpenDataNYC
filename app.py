

import sys
print(sys.executable)
import dash_mantine_components as dmc
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table, State,_dash_renderer
from datetime import date
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import folium
import io
from io import BytesIO
import base64

# Explicitly set React version
_dash_renderer._set_react_version("18.2.0")

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
update_date = date(2024, 12, 31)

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=dmc.styles.ALL,
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
server = app.server

app.title = "311 Blocked Bike Lane Dashboard"

# App layout
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    children=[
        html.Div([
            # Burger button with a drawer
            dmc.Group([
                dmc.Burger(id="burger-menu", opened=False,color="purple"),
                dmc.Text("311 Blocked Bike Lane Dashboard", size="xl")
            ], style={"alignItems": "center", "marginBottom": "20px", "backgroundColor": "#DABC94"}),

            # Drawer for navigation menu
            dmc.Drawer(
                id="drawer",
                title="Navigation Menu",
                padding="md",
                size="sm",
                children=[
                    dmc.Menu(
                        children=[
                            dmc.MenuItem("Dashboard", id="drawer-tab-1"),
                            dmc.MenuItem("About", id="drawer-tab-2"),
                        ]
                    )
                ],
                style={"backgroundColor": "#f8f9fa"},
                withCloseButton=True
            ),

            # Main Tabs for content
            dmc.Tabs(
                id="tabs",
                value="tab-1",  # Default tab to open
                children=[
                    # Tab 1 content
                    dmc.TabsPanel(
                        value="tab-1",
                        children=[
                            dmc.Text(
                                f"Each record is a 311 Service Request for 'Blocked Bike Lane' Violation. "
                                f"This dashboard explores NYPD response. **Last Updated: {update_date}**"
                            ),
                            html.Div(className="container", children=[
                                dmc.Text("Select Parameters", ta="center", size="lg"),
                                html.Div([
                                    # Start Date
                                    dmc.DatePickerInput(
                                        id="start-date",
                                        label="Start Date",
                                        #description="Select the start date",
                                        value=date(2023, 1, 1).isoformat(),
                                        minDate=date(2021, 1, 1).isoformat(),
                                        maxDate=update_date.isoformat(),
                                        style={"marginRight": "20px", "marginBottom": "5px"}
                                    ),
                                    # End Date
                                    dmc.DatePickerInput(
                                        id="end-date",
                                        label="End Date",
                                        #description="Select the end date",
                                        value=update_date.isoformat(),
                                        minDate=date(2021, 1, 1).isoformat(),
                                        maxDate=update_date.isoformat(),
                                        style={"marginBottom": "20px"}
                                    ),
                                ], style={"display": "flex", "flexDirection": "row", "marginBottom": "2px"}),
                                # Dropdown
                                html.Div([
                                    dmc.Select(
                                        id="dropdown",
                                        label="Select Community Board",
                                        placeholder="Choose an option",
                                        data=[{"label": opt, "value": opt} for opt in board_options],
                                        value="All",
                                        style={"width": "300px", "marginBottom": "2px"},
                                        clearable=True
                                    ),                                
                                ])
                            ]),
                            html.Div(className="container", children=[
                                dcc.Markdown("### How does NYPD respond?", style={'textAlign': 'center'}),
                                dcc.Graph(id="pie"),
                            ]), 
                        ],
                    ),
                    # Tab 2 content
                    dmc.TabsPanel(
                        value="tab-2",
                        children=[
                            dmc.Text("B-Man", ta="center", size="lg"),
                            dmc.Text("""
                                ### Motivation:
                                Explore and analyze NYC blocked bike lane reports.
                            """),
                        ]
                    ),
                ]
            ),
        ])
    ]
)

#C1
# Callback to update plot based on input
@callback(
    Output("pie", "figure"),
    [Input('start-date', 'value'), 
     Input('end-date', 'value'), 
     Input("dropdown", "value")
     #,Input("radio", "value")
     ]
)
def update_graph(start_date, end_date, value):
    # Ensure start_date and end_date are valid
    if start_date is None:
        start_date = date(2023, 1, 1)  # Default to the minimum date in the dataset
    else:
        start_date = pd.to_datetime(start_date).date()

    if end_date is None:
        end_date = date(2024, 12, 31)  # Default to the maximum date in the dataset
    else:
        end_date = pd.to_datetime(end_date).date()

    # Apply all filters: community board and date range
    filtered_df = df.copy()
    if value != "All":
        filtered_df = filtered_df[filtered_df["cboard_expand"] == value]

    filtered_df = filtered_df[
        (filtered_df["dateTime"] >= start_date) &
        (filtered_df["dateTime"] <= end_date)
    ]


    # Shortcut Renaming
    def valueT():
        if value != "All":
            return value.split(':')[0]
        else:
            return "All"

    # Check if filtered_df is empty
    if filtered_df.empty:
        # Handle case where no data matches the filters
        fig = px.pie(
            names=["No Data"],
            values=[1],
            title="No data available for the selected parameters."
        )
    else:
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
        title=f"Total Resolutions for {valueT()}: {filtered_df['index_'].sum()}"
    )

    # Adjust the layout for the legend
    fig.update_layout(
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='top',
            y=-0.15,  # Position below the chart
            xanchor='center',
            x=0.5  # Centered horizontally
        ),
        title_x=0.5,
        margin=dict(t=50, b=100)  # Adjust margins to make space for the legend
    )

    return fig




#Formmatting
# Combined callback for drawer and tabs
@app.callback(
    [Output("drawer", "opened"), Output("tabs", "value")],
    [Input("burger-menu", "opened"),
     Input("drawer-tab-1", "n_clicks"),
     Input("drawer-tab-2", "n_clicks")],
    prevent_initial_call=True
)
def handle_drawer_and_tabs(opened, tab1_clicks, tab2_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "tab-1"  # Default behavior
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Toggle drawer or switch tabs based on input
    if triggered_id == "burger-menu":
        return opened, dash.no_update  # Toggle drawer
    elif triggered_id == "drawer-tab-1":
        return False, "tab-1"  # Close drawer and switch to Tab 1
    elif triggered_id == "drawer-tab-2":
        return False, "tab-2"  # Close drawer and switch to Tab 2
    
    return False, "tab-1"  # Fallback behavior

# Callback to highlight the selected menu item
@app.callback(
    [Output("drawer-tab-1", "style"),
     Output("drawer-tab-2", "style")],
    [Input("drawer-tab-1", "n_clicks"),
     Input("drawer-tab-2", "n_clicks")],
    prevent_initial_call=True
)
def highlight_menu_item(tab1_clicks, tab2_clicks):
    ctx = dash.callback_context
    default_style = {"cursor": "pointer", "backgroundColor": "transparent", "padding": "10px"}
    highlight_style = {"cursor": "pointer", "backgroundColor": "#007bff", "color": "white", "padding": "10px"}
    
    if not ctx.triggered:
        return default_style, default_style
    
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "drawer-tab-1":
        return highlight_style, default_style
    elif triggered_id == "drawer-tab-2":
        return default_style, highlight_style
    
    return default_style, default_style  # Fallback


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
