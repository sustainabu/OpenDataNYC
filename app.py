import sys
print(sys.executable)

import dash
import dash_mantine_components as dmc
from dash import Dash, html, Output, Input, _dash_renderer

# Explicitly set React version
_dash_renderer._set_react_version("18.2.0")

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=dmc.styles.ALL,
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
server = app.server

# App layout
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    children=[
        html.Div([
            # Burger button with a drawer
            dmc.Group([
                dmc.Burger(id="burger-menu", opened=False),
                dmc.Text("311 Blocked Bike Lane Dashboard", size="xl")
            ], style={"alignItems": "center", "marginBottom": "20px"}),

            # Drawer for navigation menu
            dmc.Drawer(
                id="drawer",
                title="Navigation Menu",
                padding="md",
                size="sm",
                children=[
                    dmc.Menu(
                        children=[
                            dmc.MenuItem("Discovery Mode", id="drawer-tab-1"),
                            dmc.MenuItem("About", id="drawer-tab-2"),
                        ]
                    )
                ],
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
                            dmc.Text("A-Man", ta="center", size="lg"),
                            dmc.Text("""
                                ### Motivation:
                                Explore and analyze NYC blocked bike lane reports.
                            """),
                        ]
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


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
