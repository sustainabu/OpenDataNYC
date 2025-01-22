from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
from datetime import date
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Dash Bootstrap components
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SANDSTONE],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'},],) #,external_stylesheets=[dbc.themes.BOOTSTRAP]) #Added
server = app.server

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "display": "flex",
    "flex-direction": "column",  # Default to vertical orientation
    "width": "100%",
    "padding": "1rem",
    "background-color": "#f8f9fa",
    "box-shadow": "0px 2px 4px rgba(0, 0, 0, 0.1)",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-top": "4rem",  # Leave space for horizontal sidebar
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/", active="exact", className="nav-item"),
                dbc.NavLink("About", href="/about", active="exact", className="nav-item"),
            ],
            pills=True,
            className="sidebar-nav",
        )
    ],
    style=SIDEBAR_STYLE,
    className="sidebar",
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

# Sidebar layout
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# Callback to render page content
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == '/':
        return html.Div([dcc.Markdown("### Introduction\nData Portion")])
    elif pathname == '/about':
        return html.Div([dcc.Markdown("### About Time!")])
    else:
        return html.Div([dcc.Markdown("### 404: Page Not Found")])

# Add CSS to make sidebar responsive
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Responsive Sidebar</title>
        {%favicon%}
        {%css%}
        <style>
            /* For desktop: horizontal sidebar */
            @media (min-width: 768px) {
                .sidebar {
                    display: flex;
                    flex-direction: row;
                    justify-content: space-between;
                    padding: 0.5rem 1rem;
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4rem;
                    z-index: 10;
                }

                .sidebar-nav {
                    display: flex;
                    flex-direction: row;
                    width: 100%;
                }

                .nav-item {
                    margin: 0 1rem;
                }
            }

            /* For mobile: vertical sidebar */
            @media (max-width: 767px) {
                .sidebar {
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    height: auto;
                }

                .nav-item {
                    margin: 0.5rem 0;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)