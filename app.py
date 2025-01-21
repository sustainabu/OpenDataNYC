from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
from datetime import date
import pandas as pd

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

    # Hidden store for triggering client-side blurring
    dcc.Store(id='blur-trigger')
])

# Callback to render tab content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-nav', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            # Header Markdown
            dcc.Markdown(
                f"Each record is a 311 Service Request for 'Blocked Bike Lane' Violation. "
                f"This dashboard explores NYPD response. **Last Updated: {update_date}**"
            ),
            html.Div(className="container", children=[
                dcc.Markdown("## Select Parameters", style={'textAlign': 'center'}),
                html.Div([
                    html.Div([
                        dcc.Markdown("**Start Date**"),
                        dcc.DatePickerSingle(
                            id='start-date',
                            min_date_allowed=date(2021, 1, 1),
                            max_date_allowed=update_date,
                            date=date(2023, 1, 1),
                            placeholder='Select Start Date'
                        ),
                    ], style={'marginRight': '20px'}),
                    html.Div([
                        dcc.Markdown("**End Date**"),
                        dcc.DatePickerSingle(
                            id='end-date',
                            min_date_allowed=date(2021, 1, 1),
                            max_date_allowed=update_date,
                            date=update_date,
                            placeholder='Select End Date'
                        ),
                    ]),
                ], style={'display': 'flex', 'flexDirection': 'row', 'marginBottom': '20px'}),
                html.Div([
                    html.H4("Select Community Board"),
                    dcc.Dropdown(board_options, value="All", id="dropdown", style={'marginBottom': 20}),
                ]),
            ]),
        ])
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

# Client-side callback to blur inputs
app.clientside_callback(
    """
    function(trigger) {
        // Select all input elements that might trigger a keyboard
        document.querySelectorAll('.DateInput_input, .Select-input').forEach(function(el) {
            el.addEventListener('focus', function() {
                el.blur();
            });
        });
        return null;
    }
    """,
    Output('blur-trigger', 'data'),  # This is a no-op output just to trigger the script
    Input('tabs-nav', 'value')  # Trigger on tab selection (or any other event)
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
