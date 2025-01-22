import dash
from dash import html, Output, Input
import dash_mantine_components as dmc
from datetime import date

app = dash.Dash(__name__)

app.layout = html.Div([
    # Date Picker Component
    dmc.DatePicker(
        id="date-picker",
        label="Select a Date",
        description="Pick a date using the dropdown or calendar.",
        value=date.today(),  # Default to today's date
        style={"width": "300px", "marginBottom": "20px"},
    ),

    # Dropdown (Select) Component
    dmc.Select(
        id="dropdown",
        label="Select an Option",
        placeholder="Choose an option",
        data=[
            {"label": "Option 1", "value": "1"},
            {"label": "Option 2", "value": "2"},
            {"label": "Option 3", "value": "3"},
        ],
        style={"width": "300px", "marginBottom": "20px"},
    ),

    # Output Container
    html.Div(id="output", style={"marginTop": "20px", "fontSize": "18px"})
])


# Callback to update the output based on user selection
@app.callback(
    Output("output", "children"),
    [Input("date-picker", "value"), Input("dropdown", "value")]
)
def update_output(selected_date, selected_option):
    if selected_date and selected_option:
        return f"Selected Date: {selected_date}, Selected Option: {selected_option}"
    elif selected_date:
        return f"Selected Date: {selected_date}, No Option Selected"
    elif selected_option:
        return f"Selected Option: {selected_option}, No Date Selected"
    else:
        return "Please select a date and an option."


if __name__ == "__main__":
    app.run_server(debug=True)
