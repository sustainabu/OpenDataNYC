import shiny
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35]
})

app_ui = shiny.ui.page_fluid(
    shiny.ui.input_select("name", "Select Name:", df["Name"].unique()),
    shiny.ui.output_data_frame("table")
)

def server(input, output, session):

    @shiny.render.data_frame
    def table():
        filtered_df = df[df["Name"] == input.name]
        return filtered_df

app = shiny.App(app_ui, server)

app.run()