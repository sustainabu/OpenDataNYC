@render.data_frame
def summary_statistics():
    return df.head(2)


@render.table
def filtered_data():
    filtered_dfs = df[(df["dateTime"] >= input.date_range()[0]) & (df["dateTime"] <= input.date_range()[1])]
    filtered_dfs = filtered_dfs[filtered_dfs["bias"] == input.ticker()]
    return filtered_dfs.head(5)

#test Code
@render.table
def tabplot1():
    p2=['month_bin','borough','index_']
    pv=f_df()[p2].groupby(['month_bin','borough']).sum().reset_index()
    pv1=pd.pivot_table(pv,index='month_bin', columns='borough', values=['index_']).reset_index().fillna(0) 
    return pv1.head(2)


#Chloromap
@render.ui
def choro_map():
    p = ['precinct', 'index_']
    mf = f_df()[p].groupby(['precinct']).sum().reset_index().fillna(0)
    mf.columns = ['precinct1', 'Count']
    
    # Choropleth Map
    NYC_map = folium.Map(location=[40.7128466, -73.9138168], zoom_start=11.25, tiles="OpenStreetMap")
    precinct_geo = r'Shapefiles_JSON/nyc-police-precincts.geojson'

    # Use folium.Choropleth instead of NYC_map.choropleth
    folium.Choropleth(
        geo_data=precinct_geo,
        data=mf,
        columns=['precinct1', 'Count'],
        key_on="feature.properties.precinct",
        fill_color='YlOrRd', 
        fill_opacity=0.7, 
        line_opacity=0.2,
        legend_name='NYC {} biased crimes)'.format(input.ticker()),
        nan_fill_color="gray",
        nan_fill_opacity=0.4,
        highlight=True
    ).add_to(NYC_map)  # Add the choropleth layer to the map
    return NYC_map  
