# import the libraries

import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import pandas as pd
import geopandas

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
from streamlit_folium import st_folium, folium_static
import folium
from folium.features import DivIcon

import re

############################################################################################################################
##########################################   Read the dataset & geojson files ##############################################
############################################################################################################################

data = pd.read_csv("airbnb_prices_in_6_european_cities.csv")

mean_prices_summary = pd.read_csv("mean_values_per_neighbourhoods.csv")

geo_amsterdam = geopandas.read_file('Amsterdam_neighbourhoods/new_neighbourhoods.geojson', driver='GeoJSON')
geo_lisbon = geopandas.read_file('Lisbon_neighbourhoods/new_neighbourhoods.geojson', driver='GeoJSON')
geo_london = geopandas.read_file('London_neighbourhoods/new_neighbourhoods.geojson', driver='GeoJSON')
geo_paris = geopandas.read_file('Paris_neighbourhoods/new_neighbourhoods.geojson', driver='GeoJSON')
geo_rome = geopandas.read_file('Rome_neighbourhoods/new_neighbourhoods.geojson', driver='GeoJSON')
geo_vienna = geopandas.read_file('Vienna_neighbourhoods/new_neighbourhoods.geojson', driver='GeoJSON')

# put all geojson files into a dictionary
geo_files = {'Amsterdam': geo_amsterdam,
             'Lisbon': geo_lisbon,
             'London': geo_london,
             'Paris': geo_paris,
             'Rome': geo_rome,
             'Vienna': geo_vienna}
############################################################################################################################
##########################################     Coordinates of the capitals     #############################################
############################################################################################################################

#[Latitude,Longitude]
capitals_lat_lng = {'Amsterdam': [52.377956,4.897070],
                    'Lisbon': [38.736946, -9.142685],
                    'London': [51.509865, -0.118092],
                    'Paris': [48.864716, 2.349014],
                    'Rome': [41.902782, 12.496366],
                    'Vienna': [48.210033, 16.363449]}

############################################################################################################################
##################################################  Define some functions  #################################################
############################################################################################################################

# This is for the map visualization using choropleth
def visualization_with_folium(df, x, center, geo_city):
    
    map = folium.Map(location=center,
                     tiles="cartodbpositron",zoom_start=10.5) 
    folium.Marker(location=center,
                  icon = folium.Icon(color='black')).add_to(map)

    folium.Choropleth(geo_data=geo_city,
                      name="choropleth",
                      data=df[x],
                      columns=["Neighbourhood", x],
                      key_on="feature.id",
                      fill_color="RdYlGn",
                      fill_opacity=0.6,
                      line_opacity=0.6,
                      legend_name="Mean of prices",).add_to(map)

    folium.LayerControl().add_to(map)
    
    for i,location in enumerate(df.Centroid.values):
        string = location[7:-1]
        pattern=' '
        match=(re.search(pattern, string))
        end, start = match.span()[0], match.span()[1]
        x = float(location[7:end])
        y = float(location[(7+start):-1])
        loc=[y+0.004,x]
        folium.map.Marker(loc, icon=DivIcon(icon_size=(20,20),
                                            icon_anchor=(0,0),
                                            html='<div style="font-size: 10pt">%s</div>' %df['Neighbourhood'][i])).add_to(map)

    return map



#  This is checking for outliers
def check_outliers(df):
    
    df = df.reset_index()
    df = df.drop("index",axis=1)
    
    lof = LocalOutlierFactor(n_neighbors=20, contamination='auto')
    good = lof.fit_predict(df.Price.to_numpy().reshape(-1,1)) == 1
    
    dropped_points = []
    for i in range(len(good)):
        if good[i]==False:
            dropped_points.append(i)
  
    df = df.drop(dropped_points, axis=0)
    df = df.reset_index()
    df = df.drop("index",axis=1)
    
    return df

############################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------ #
############################################################################################################################
###################################################  Start of the code  ####################################################
############################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------ #
############################################################################################################################


st.set_page_config(layout="wide")
st.write("## This Web App shows data related to the prices of airbnb listings in 6 european cities")
st.write("###### Created by Antonios Raptakis")

st.write("The csv files has been taken by kaggle and the geojson files by Inside Airbnb. The Room type indicates the kind of hosting with 2 options available, Entire home vs Private room.")

cities = data.City.unique()
st.markdown("##### At the dropdown below you can select the city and see the results.")
specify_the_city = st.selectbox("Select the city", cities,0)

explain_boxplot = '<p style="text-align: left; font-size: 20px;">For the boxplots below, I have applied the LocalOutlierFactor from the neighbours of scikit-learn, in order to drop off the outliers. However, for the calculation of the mean of prices per room type and neighbourhood, and the overall mean, all of the values have been counted in.</p>'
st.write(explain_boxplot, unsafe_allow_html=True)


# start by splitting the App into two columns
col1, col2 = st.columns((1,1))

# Pie Plot for Room type
with col1:
    
    fig = px.pie(data[data.City==specify_the_city], values='Price', names='Room type', 
                 color_discrete_sequence=['firebrick','steelblue'])
    fig.update_layout(legend=dict(x=0,y=1.2, title_font_family="Times New Roman", font=dict(size= 20)),
                      margin=dict(t=120, b=120, l=120, r=120), title_text="Room type", title_x=0.4)
    fig.update_traces(pull=0.1, textfont_size=20)
    st.plotly_chart(fig)

    
# Copy the original dataset and apply the function which checks for outliers
data_copy = data[data.City==specify_the_city].copy()
data_without_outliers = check_outliers(data_copy)

# Boxplot for the person capacity
with col2:
    
    fig = px.box(data_without_outliers, x="Person capacity", y="Price", color="Room type",
                 color_discrete_sequence=['steelblue','firebrick'])
    fig.update_layout(title_text="Comparison of prices for different capacity and room type", title_x=0.15)
    fig.update_traces(quartilemethod="exclusive")
    st.plotly_chart(fig, use_container_width=True)
    
############################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------ #
############################################################################################################################

# In a single row, show the boxplots comparison per neighbourhood and person capacity 
fig = px.box(data_without_outliers, x="Neighbourhood", y="Price", color="Room type",
                 color_discrete_sequence=['steelblue','firebrick'])
fig.update_layout(title_text="Comparison of prices between neighbourhoods and room type", title_x=0.3)
fig.update_traces(quartilemethod="exclusive")
st.plotly_chart(fig, use_container_width=True)

############################################################################################################################   
# ------------------------------------------------------------------------------------------------------------------------ #
############################################################################################################################

explain_the_maps = '<p style="text-align: center; font-size: 18px;">The maps below show the airbnb options with different colors on the left and the overall mean per neighbourhood on the right side, and have been created using folium. You can zoom in and out by using the +/- on top left of the map.</p>'
st.write(explain_the_maps, unsafe_allow_html=True)


# split again into two columns
col4, col5 = st.columns((1,1))
   
# create a new dataframe by giving the city that you want to explore
new_set_city = mean_prices_summary[mean_prices_summary.City==specify_the_city]
new_set_city.reset_index(inplace=True)
new_set_city = new_set_city.drop("index",axis=1)


# Map visualization with all of the airbnb listings of the specific city by highlighting the neighbourhoods
with col4:
    column_title = '<p style="text-align: center; font-size: 17px;">Points: Red: Entire home vs Blue: Private room</p>'
    col4.write(column_title, unsafe_allow_html=True)
   
    map = folium.Map(location=capitals_lat_lng[specify_the_city],
                     tiles="cartodbpositron",zoom_start=10.5) 
    folium.Marker(location=capitals_lat_lng[specify_the_city]).add_to(map)


    for i in range(len(data[data.City==specify_the_city]['Latitude'])):
        dataset = data[data.City==specify_the_city]
        dataset = dataset.reset_index().drop(columns="index")
        latitude = dataset[dataset.City==specify_the_city]['Latitude'][i]
        longitude = dataset[dataset.City==specify_the_city]['Longitude'][i]
        if dataset['Room type'][i]=='Entire home':
            folium.CircleMarker(location=[latitude,longitude],radius=6,fill_color="red",
                                opacity=0.8,fill_opacity=0.4,fill=True,color=True).add_to(map)
        else:
            folium.CircleMarker(location=[latitude,longitude],radius=6,fill_color="blue",
                                opacity=0.8,fill_opacity=0.4,fill=True,color=True).add_to(map)
                

    for _, r in geo_files[specify_the_city].iterrows():
        sim_geo = geopandas.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'green'})
        folium.Popup(r['Neighbourhood']).add_to(geo_j)
        geo_j.add_to(map)  
        
    folium_static(map, width=600, height=400)

    
# Map visualization which shows the overall mean values of the prices per neighbourhood. 
with col5:
    column_title = '<p style="text-align: center; font-size: 17px;">Overall Mean</p>'
    col5.write(column_title, unsafe_allow_html=True)
    map_ent_home = visualization_with_folium(new_set_city,
                                             'Overall Mean',
                                             capitals_lat_lng[specify_the_city],
                                             geo_files[specify_the_city])

    folium_static(map_ent_home, width=600, height=400)
    
############################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------ #
############################################################################################################################

explain_the_maps = '<p style="text-align: center; font-size: 18px;">The maps below show the mean prices per neighbourhood for the different room type options, Entire home on the left on the left vs Private room on the right side. In case of a neighbourhood with dark grey color (outside the colors of the indicated spectrum), it means that this neighbourhood has no airbnb with that option.</p>'
st.write(explain_the_maps, unsafe_allow_html=True)


# split again into two columns
col6, col7 = st.columns((1,1))


# Map visualization which shows the mean values of prices for the Entire home option of room type per neighbourhood. 
with col6:
    column_title = '<p style="text-align: center; font-size: 20px;">Entire home</p>'
    col6.write(column_title, unsafe_allow_html=True)
    map_ent_home = visualization_with_folium(new_set_city,
                                             'Mean Ent. home',
                                             capitals_lat_lng[specify_the_city],
                                             geo_files[specify_the_city])
    
    folium_static(map_ent_home, width=600, height=400)


# Map visualization which shows the mean values of prices for the private room option of room type per neighbourhood. 
with col7:
    column_title = '<p style="text-align: center; font-size: 20px;">Private room</p>'
    col7.write(column_title, unsafe_allow_html=True)
    map_private_room = visualization_with_folium(new_set_city,
                                                 'Mean Priv. room',
                                                 capitals_lat_lng[specify_the_city],
                                                 geo_files[specify_the_city])
    
    folium_static(map_private_room, width=600, height=400)    
    
############################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------ #
############################################################################################################################

# create a new dataframe by giving the city that you want to explore
mean_city_neighbourhood = mean_prices_summary[mean_prices_summary.City==specify_the_city]
mean_city_neighbourhood.reset_index(inplace=True)
mean_city_neighbourhood = mean_city_neighbourhood.drop("index",axis=1)

# show the barplots comparison between the mean of private room vs entire home per neighbourhood and create a line which shows
# the overall mean
x = list(range(len(mean_city_neighbourhood['Neighbourhood'])))
bar_line_plots = [go.Bar(x=x, y=new_set_city['Mean Priv. room'], name='Private room',
                         marker=go.bar.Marker(color='steelblue')),
                  go.Bar(x=x, y=new_set_city['Mean Ent. home'], name='Entire home',
                         marker=go.bar.Marker(color='firebrick')),
                  go.Scatter(x=x, y=new_set_city['Overall Mean'], name='Overall mean',
                             line=dict(color="black"))]
    
layout = go.Layout(xaxis_tickvals = x,
                   xaxis_ticktext = new_set_city['Neighbourhood'].values,
                   xaxis_title="Neighbourhood",
                   yaxis_title="Mean Price",
                   title="Comparison of the mean of prices and overall mean between the neighbourhoods and room type",
                   title_x=0.22)

# Make the multi-bar plot
fig = go.Figure(data=bar_line_plots, layout=layout)

st.plotly_chart(fig, use_container_width=True)