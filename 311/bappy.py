from shiny.express import input, render, ui
#import pandas as pd
#import numpy as py



# Create the DataFrame
#hf = pd.DataFrame(data)

# Inputting Slideer
ui.input_slider("val", "Slider label", min=0, max=100, value=50)

#Inputting Drop Down
#ui.input_selectize(
#    "var", "Select variable",
#    choices=["bill_length_mm", "body_mass_g"]
#)


#Outputting
@render.text
def slider_val():
    return f"Slider value: {input.val()}"

#@render.plot
#def hist():
#    from matplotlib import pyplot as plt
#    from palmerpenguins import load_penguins

#    df = load_penguins()
#    df[input.var()].hist(grid=False)
#    plt.xlabel(input.var())
#    plt.ylabel("count")

#@render.data_frame
#def data():
#    return hf()

#@render.data_frame
# def head():
    #from palmerpenguins import load_penguins
   # df = load_penguins()
    #return df[["species", input.var()]]
