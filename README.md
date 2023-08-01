Airbnb is an American San Francisco-based company operating an online marketplace for short-term homestays and experiences. It started at 2008 and nowdays shares a non ignorable percentage of the respective market worldwide. More and more people provide a flat or house to the platform. The client can select different hosting options, which are provided in the platform.

My motivation to create this dashboard was to compare the airbnb prices between the different room types on neighbourhoods of 6 european cities, Amsterdam-Lisbon-London-Paris-Rome-Vienna. The dataset has been taken by kaggle and from the link below I only take weekdays file:

https://www.kaggle.com/datasets/thedevastator/airbnb-price-determinants-in-europe?select=london_weekdays.csv

For the geojson files, I used the files from http://insideairbnb.com.

The libraries that I used for the WebApp:

- Numpy
- Pandas
- Scikit-learn
- Plotly
- Folium
- Geopandas
- Streamlit

In order to run the WebApp in the streamlit cloud, I had to use the file requirements.txt with the name of some libraries that I use in the python script.

The directories with the european cities include the geojson files and the Jupyter_Notebook directory includes two notebooks, one creates the airbnb_prices_in_6_european_cities.csv while the other the mean_values_per_neighbourhoods.csv and the new geojson files.



# Link to the WebApp #: https://antoniosraptakis-dashboard--airbnb-for-6-european-cities-xcetuq.streamlit.app
