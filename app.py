
import dash_mantine_components as dmc
from datetime import date
import pandas as pd
from dash import Dash, html, Output, Input,_dash_renderer
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

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=dmc.styles.ALL )
server = app.server

app.title = "311 Blocked Bike Lane Dashboard"
update_date = date(2024, 12, 31)

# App layout
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    children= [
        html.Div([
            dmc.Tabs([
                dmc.TabsList([
                    dmc.TabsTab("Discovery Mode", value="tab-1"),
                    dmc.TabsTab("About", value="tab-2"),
                ]),
                dmc.TabsPanel(
                    value="tab-1",
                    children=[
                        dmc.Text(
                            f"Each record is a 311 Service Request for 'Blocked Bike Lane' Violation. "
                            f"This dashboard explores NYPD response. **Last Updated: {update_date}**"
                        ),
                        dmc.Text("Select Parameters", ta="center", size="lg"),
                        html.Div([
                            # Start Date
                            dmc.DatePickerInput(
                                id="start-date",
                                label="Start Date",
                                description="Select the start date",
                                value=date(2023, 1, 1).isoformat(),
                                minDate=date(2021, 1, 1).isoformat(),
                                maxDate=update_date.isoformat(),
                                style={"marginRight": "20px", "marginBottom": "20px"}
                            ),
                            # End Date
                            dmc.DatePickerInput(
                                id="end-date",
                                label="End Date",
                                description="Select the end date",
                                value=update_date.isoformat(),
                                minDate=date(2021, 1, 1).isoformat(),
                                maxDate=update_date.isoformat(),
                                style={"marginBottom": "20px"}
                            ),
                        ], style={"display": "flex", "flexDirection": "row", "marginBottom": "20px"}),

                        # Dropdown
                        dmc.Select(
                            id="dropdown",
                            label="Select Community Board",
                            placeholder="Choose an option",
                            data=[{"label": opt, "value": opt} for opt in board_options],
                            value="All",
                            style={"width": "300px", "marginBottom": "20px"},
                            clearable=True
                        ),
                    ],
                ),
                dmc.TabsPanel(
                    value="tab-2",
                    children=[
                        dmc.Text("Select Parameters", ta="center", size="lg"),
                        dmc.Text("""
                            ### Motivation:
                            Explore and analyze NYC blocked bike lane reports.
                        """),
                    ],
                ),
            ])
        ])
    ]
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
