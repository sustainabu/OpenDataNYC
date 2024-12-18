from shiny import App, ui, reactive, render
from shinywidgets import render_plotly
import plotly.express as px
import pandas as pd
import folium
import json
from pathlib import Path

# 1. Load data
app_dir = Path(__file__).parent
df = pd.read_csv(app_dir / "dfc_out.csv")
with open(app_dir / "CommunityDistricts.geojson", "r") as f:
    cboard_geo = json.load(f)

# Prepare data
df['dateTime'] = pd.to_datetime(df['dateTime'], format='%Y-%m-%d').dt.date
board_options = ["All"] + sorted(df['cboard_name'].dropna().unique())

# 2. UI Configuration
app_ui = ui.page_fluid(
    ui.h1("311 Blocked Bike Lane Service Request Dashboard by Abu Nayeem"),
    ui.nav_spacer()  # Add other elements here
)

with ui.page_fluid():
    ui.include_css(app_dir / "styles.css")  # Custom CSS for further styling

    with ui.sidebar(collapsible=True):  # Collapsible sidebar for better mobile layout
        ui.input_date_range(
            "date_range", "Select date range",
            start="2023-01-01", min="2023-01-01"
        )
        ui.input_selectize(
            "ticker", "Select community board",
            choices=board_options, selected="All"
        )
        ui.input_numeric("obs", "Min. Entries for Map Display", 3, min=1, max=10)

    # Dashboard content
    with ui.nav_panel("Dashboard"):
        ui.markdown("""
        **View Analysis**: [Interactive Report](https://example.com/report)  
        """)
        with ui.navset_card_underline():
            with ui.nav_panel("Data"):
                @render.plot
                def line_chart():
                    # Dynamic chart sizing for responsiveness
                    fig = px.line(
                        df, x="dateTime", y="MinutesElapsed", title="Response Time Trends",
                        labels={"dateTime": "Date", "MinutesElapsed": "Minutes"}
                    )
                    fig.update_layout(
                        width="100%", height=400,  # Responsive chart dimensions
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    return fig

            with ui.nav_panel("Interactive Map"):
                @render.ui
                def interactive_map():
                    # Dynamic map sizing and configuration
                    map_ = folium.Map(location=[40.7128, -74.0060], zoom_start=11, tiles="CartoDB positron")
                    return map_

            with ui.nav_panel("Table"):
                @render.data_frame
                def summary_table():
                    return df.head(20)

    with ui.nav_panel("About"):
        ui.markdown("This app showcases 311 bike lane service requests.")

# 3. Reactive Logic
@reactive.calc
def filtered_data():
    data = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    if input.ticker() != "All":
        data = data[data["cboard_name"] == input.ticker()]
    return data

# 4. CSS Adjustments for Responsiveness
with open(app_dir / "styles.css", "w") as css_file:
    css_file.write("""
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }
    .container {
        max-width: 100%; /* Full width for mobile */
        margin: 0 auto;
        padding: 1rem;
    }
    .sidebar {
        width: 100%; /* Sidebar takes full width on smaller screens */
    }
    .nav-panel {
        margin: 1rem;
    }
    @media (max-width: 768px) {
        .sidebar {
            display: none; /* Collapsible for smaller screens */
        }
    }
    """)

# 5. Run App
app = App(ui, reactive)