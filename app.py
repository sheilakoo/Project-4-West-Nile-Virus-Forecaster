### --- IMPORT LIBRARIES --- ###
# Libraries
from pathlib import Path
import streamlit as st
from streamlit_option_menu import option_menu
from urllib.request import urlopen
import pickle
import pandas as pd
import numpy as np
import json
import math
import requests
import sys
import plotly.express as px
import geopandas as gpd
from geopy.geocoders import Nominatim
import folium
from datetime import datetime, timedelta

### --- IMPORT DATA --- ###
## spray_df
spray_path = Path(__file__).parent / "spray_df.csv"
spray_df = pd.read_csv('spray_df.csv')

## train_df
train_path = Path(__file__).parent / "train_df.csv"
train_df = pd.read_csv('train_df.csv')

## weather_df
weather_path = Path(__file__).parent / "weather_df.csv"
weather_df = pd.read_csv('weather_df.csv')

## Chicago map GEOJSON file
chicago_path = Path(__file__).parent / "boundaries_chicago.geojson"
chicago_city = gpd.read_file('boundaries_chicago.geojson')

### --- FUNCTIONS --- ###

# Function for mapping traps and spraying locations
def spray_and_trap_locations(train_df, spray_df):

        # Create a map of Chicago
        chicago_city = [41.881832, -87.623177]
        Map = folium.Map(location=chicago_city, tiles="Stamen Terrain", zoom_start=11)
        
        # Separate out geographical data into new dataframe for mapping
        map_train = train_df[['trap','latitude','longitude']]
        
        # Get a unique list of all traps and their GPS coordinates
        map_train.drop_duplicates('trap', keep='first', inplace=True)
        
        # Separate out geographical data into new dataframe for mapping
        map_spray = spray_df[['latitude', 'longitude']].apply(lambda x: round(x, 3))
        
        # Create a new var of location as the intersection of longitude and latitude
        map_spray['loc']=round(abs(map_spray['longitude']) + map_spray['latitude'],3)
        
        # Get a unique list of all spraying locations 
        map_spray.drop_duplicates('loc', keep="first",inplace=True)
        
        # Plot the traps as blue labels
        for i in range(len(map_train['trap'])):
            folium.Marker([map_train.iloc[i]['latitude'], map_train.iloc[i]['longitude']], popup=map_train.iloc[i]['trap']).add_to(Map)
        
        # Plot spraying locations as green labels
        for i in range(len(map_spray['loc'])):
            folium.Marker([map_spray.iloc[i]['latitude'],map_spray.iloc[i]['longitude']], popup=map_spray.iloc[i]['loc'],icon=folium.Icon(color='green')).add_to(Map)

        return Map

### --- WEB LAYOUT --- ###
# Configure webpage
st.set_page_config(
    page_title='Chicago West Nile Virus Control',
    page_icon='mosquito',
    layout='wide',
    initial_sidebar_state='expanded'
    )

### --- HEADER --- ###
st.markdown("""
    <h1 style='text-align: center; font-size: 70px;'>Chicago West Nile Virus Control</h1>
""", unsafe_allow_html=True)

### --- TOP NAVIGATION BAR --- ###
selected = option_menu(
    menu_title = None,
    options = ['About', 'Trends', 'Surveillance', 'Control Measures', 'Contact Us'],
    icons = ['eject', 'bar-chart', 'binoculars', 'spray-can', 'phone'],
    menu_icon = 'mosquito',
    default_index = 0,
    orientation = 'horizontal',
    styles={
        'nav-link-selected': {'background-color': '#89b5ffff'},
        }
)

if selected == 'About':
    st.title('About')
    style = "<div style='background-color:#2C78DA; padding:2px'></div>"
    st.markdown(style, unsafe_allow_html = True)    
    ### INSERT BACKGROUND INFO HERE ###

if selected == 'Trends':
    st.title('Trends')

    ### --- WHAT (WHAT SPECIES) --- ###

    ### --- WHERE (LOCATION AND TRAP) --- ###

    st.subheader('Mosquito Population By Community')
    with open("mos_heatmap.html", "r") as f:
        html_code = f.read()
    st.components.v1.html(html_code, width=700, height=500)

    st.subheader('Vector Control Measures')
    with open("spray_trap_locations.html", "r") as f:
        html_code = f.read()
    st.components.v1.html(html_code, width=700, height=500)

    ### --- WHEN (WHAT TIME OF THE YEAR? --- ###
    

if selected == 'Surveillance':
    st.title('Surveillance')
    style = "<div style='background-color:#2C78DA; padding:2px'></div>"
    st.markdown(style, unsafe_allow_html = True)

    # API key - stored in .streamlit folder

    api_key = st.secret['1f719a14f54502679763803e8fbc624c']

    # API CALL from the Open Weather Map webpage
    url = 'https://api.openweathermap.org/data/2,5/weather?q={}&appid={}'
    url_1 = 'https://api.openweathermap.org/data/2,5/onecall/timemachine?lat={}&lon={}&dt={}&appid={}'

    # Create a function to get the weather data
    def getweather(city):
        result = requests.get(url.format(city, api_key))
        if result:
            json = result.json()
            #st.write(json)
            country = json['sys']['country']
            temp = json['main']['temp'] - 273.15
            humidity = json['main']['humidity'] - 273.15
            icon = json['weather'][0]['icon']
            lon = json['coord']['lon']
            lat = json['coord']['lat']
            des = json['weather'][0]['description'] 
            res = [country, round(temp, 1), humidity, icon, lon, lat, des]
            return res, json
        else:
            print('Error in search!')

    # Create a fuction to get historical data
    def getweather_historical(lat, lon, start):
        res = requests.get(url_1.format(lat, lon, start, api_key))
        data = res.json()
        temp - []
        for i in range(24):
            temp.append(data['hourly'][i]['temp'])
            return data, temp
        
    col1, col2 = st.beta_columns(2)

    with col1:
        address = st.text_input('Please enter address')

    with col2:
        if address:
            res, json = getweather(address)
            #st.write(res)
            st.success('Current: ' + str(round(res[1],2)))
            #st.info('Humidity: ' + str(round(res[3],2)))
            st.subheader('Status: ' + str(res[6]))
            web_str = '![Alt Text]' + '(http://openweathermap.org/img/w/' + res[3] + '.png)'
            st.markdown(web_str)

    # Fetch weather data when the user clicks the button
    #if st.button("Get Weather Forecast"):
    #    if address:
    #        get_weather(address)
    #    else:
    #        st.write("Please enter your address.")


    ### --- DATE --- ###
    ## 'Date' header
    st.subheader('Date')

    ## Create columns
    col1, col2 = st.columns(2)

    ## 'Month'
    with col1:

        ### Create 'Month' options
        month_options = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

        ### Create 'Month' selection dropdown
        month_selected = st.selectbox('Select Month', month_options)

    ## 'Year'
    with col2:
        ### Create 'Year' options
        year_options = [2007, 2008, 2009 ,2010, 2011, 2012, 2013]

        ### Create 'Year' selection dropdown
        year_selected = st.selectbox('Select Year', year_options)


    ### --- LOCATION --- ###
    ## Create 'Location' header
    st.header('Location')

    ## 'Address'
    ## Create columns
    col1, col2, col3 = st.columns(3)

    with col1:
        ### Create 'Address' sub-header
        st.subheader('Address')

        ### Create 'Address' options
        address_options = ['4100  N OAK PARK AVE, Chicago, IL',
                        '6200  N MANDELL AVE, Chicago, IL',
                        '7900  W FOSTER AVE, Chicago, IL', 
                        '1500  W WEBSTER AVE, Chicago, IL',
                        '2500  W GRAND AVE, Chicago, IL',
                        '1100  W ROOSEVELT, Chicago, IL',
                        '1100  W CHICAGO, Chicago, IL',
                        '2100  N STAVE ST, Chicago, IL',
                        '2200  N CANNON DR, Chicago, IL',
                        '2200  W 113TH ST, Chicago, IL',
                        '1100  S PEORIA ST, Chicago, IL',
                        '1700  W 95TH ST, Chicago, IL',
                        '2200  W 89TH ST, Chicago, IL',
                        '5300  N STREETER DR, Chicago, IL',
                        '6500  N OAK PARK AVE, Chicago, IL',
                        '7500  N OAKLEY AVE, Chicago, IL',
                        '1500  N LONG AVE, Chicago, IL',
                        '8900  S CARPENTER ST, Chicago, IL',
                        '9100  W HIGGINS AVE, Chicago, IL',
                        '3600  N PITTSBURGH AVE, Chicago, IL',
                        '7200  N OKETO AVE, Chicago, IL',
                        '3800  N CALIFORNIA AVE, Chicago, IL',
                        '4900  W BALMORAL AVE, Chicago, IL',
                        '5800  N WESTERN AVE, Chicago, IL',
                        '5000  S CENTRAL AVE, Chicago, IL',
                        '1400  N HUMBOLDT DR, Chicago, IL',
                        '1000  S VINCENNES, Chicago, IL',
                        '1100  S ASHLAND AVE, Chicago, IL',
                        '1100  S STATE ST, Chicago, IL',
                        '4200  W 127TH PL, Chicago, IL',
                        '5300  W AGATITE AVE, Chicago, IL',
                        '4000  N AUSTIN AVE, Chicago, IL',
                        '4300  N ASHLAND AVE OVERPASS, Chicago, IL',
                        '4200  N RICHMOND ST, Chicago, IL', 
                        '2800  N FRANCISCO AVE, Chicago, IL',
                        '1500  W GRANVILLE AVE, Chicago, IL',
                        '1800  W FARWELL AVE, Chicago, IL',
                        '7000   W ARMITAGE AVENUE, Chicago, IL',
                        '2500  S MILLARD AVE, Chicago, IL',
                        '2100  N LAWLER AVE, Chicago, IL',
                        '3500  W 116TH ST, Chicago, IL',
                        '9300  S DR MARTIN LUTHER KING JR DR, Chicago, IL',
                        '3700  N KEDVALE AVE, Chicago, IL', 
                        '4500  N CAMPBELL AVE, Chicago, IL',
                        '4000  N TRIPP AVE, Chicago, IL', 
                        '4600  N MILWAUKEE AVE, Chicago, IL',
                        '6000  N AVONDALE AVE, Chicago, IL', 
                        '7000  N MOSELL AVE, Chicago, IL', 
                        '6100  N LEMONT AVE, Chicago, IL', 
                        '2700  S WESTERN AVE, Chicago, IL',
                        '6800  W BELDEN AVE, Chicago, IL', 
                        '2100  S HAMLIN AVE, Chicago, IL',
                        '3000  W 18TH ST, Chicago, IL', 
                        '1100  S CALIFORNIA, Chicago, IL',
                        '2500  S THROOP, Chicago, IL', 
                        '1000  W 95TH ST, Chicago, IL',
                        '1000  S CALIFORNIA AVE, Chicago, IL', 
                        '9600  S HOYNE AVE, Chicago, IL',
                        '1800  W LELAND AVE, Chicago, IL', 
                        '6100  W FULLERTON AVE, Chicago, IL',
                        '6400  W STRONG ST, Chicago, IL', 
                        '1200  W GREENLEAF AVE, Chicago, IL',
                        '1000  N CENTRAL PARK DR, Chicago, IL',
                        '2000  E 111TH ST, Chicago, IL',
                        '3300  N RUTHERFORD AVE, Chicago, IL', 
                        '1100  S ARTESIAN AVE, Chicago, IL',
                        '6000  W ROSCOE ST, Chicago, IL',
                        '6000  W MONTROSE DR, Chicago, IL',
                        '3300  E RANDOLPH ST, Chicago, IL',
                        '3300  W 104TH ST, Chicago, IL',
                        '4900  W SUNNYSIDE AVE, Chicago, IL', 
                        '3000  S HOYNE AVE, Chicago, IL',
                        '4200  W 31ST ST, Chicago, IL', 
                        '1700  N PULASKI RD, Chicago, IL',
                        '2200  W PERSHING RD, Chicago, IL', 
                        '2200  W 51ST ST, Chicago, IL',
                        '3500  W 51ST ST, Chicago, IL', 
                        '5200  W 63RD ST, Chicago, IL'
                        '6700  S KEDZIE AVE, Chicago, IL', 
                        '7300  S CICERO AVE, Chicago, IL'
                        '2200  W 69TH ST, Chicago, IL',
                        '5200  S NORDICA, Chicago, IL',
                        '6100  S MELVINA AVE, Chicago, IL',
                        '1000  E 67TH ST, Chicago, IL',
                        '3900  S ASHLAND AVE, Chicago, IL',
                        '4700  S CORNELL AVE, Chicago, IL',
                        '5500  S DR MARTIN LUTHER KING JR DR, Chicago, IL',
                        '6400  S STONY ISLAND AVE, Chicago, IL',
                        '7100  S SOUTH SHORE DR, Chicago, IL',
                        '7700  S EBERHART AVE, Chicago, IL',
                        '4000  S DEARBORN ST, Chicago, IL',
                        '5000  S UNION AVE, Chicago, IL',
                        '7900  S CHICAGO AVE, Chicago, IL',
                        '5200  S KOLMAR, Chicago, IL',
                        '6300  W 64TH ST, Chicago, IL',
                        '3700  S PULASKI RD, Chicago, IL',
                        '1200  S DOTY AVE, Chicago, IL',
                        '1000  S STONY ISLAND AVE, Chicago, IL',
                        '1300  S TORRENCE AVE, Chicago, IL',
                        '1300  S MACKINAW, Chicago, IL',
                        '1300  S BRANDON, Chicago, IL',
                        '3700  E 118TH ST, Chicago, IL',
                        '3800  E 115TH ST, Chicago, IL',
                        '8100  E 91ST ST, Chicago, IL',
                        '2400  E 105TH ST, Chicago, IL',
                        '8000  S KEDZIE AVE, Chicago, IL',
                        '6500  S RACINE AVE, Chicago, IL',
                        '8200  E 138TH ST, Chicago, IL',
                        '8900  S MUSKEGON AVE, Chicago, IL',
                        '9800  S AVENUE G, Chicago, IL',
                        '1000  S COTTAGE GROVE, Chicago, IL',
                        '1100  S AVENUE L, Chicago, IL',
                        '5800  N PULASKI RD, Chicago, IL',
                        '6600  S KILPATRICK AVE, Chicago, IL',
                        '8100  W 37TH PL., Chicago, IL',
                        '4000  E 130TH ST, Chicago, IL',
                        '9100  W HIGGINS RD, Chicago, IL',
                        '1000  W OHARE AIRPORT, Chicago, IL',
                        '1000  W OHARE, Chicago, IL',
                        '4800  W MONTANA ST, Chicago, IL',
                        '5100  N MONT CLARE AVE, Chicago, IL',
                        '8200  S KOSTNER AVE, Chicago, IL',
                        '6500  E 91ST PL, Chicago, IL',
                        '1700  W ADDISON ST, Chicago, IL',
                        '9000  W GARFIELD BLVD, Chicago, IL',
                        '1100  S WALLACE ST, Chicago, IL',
                        '1300  N LARAMIE AVE, Chicago, IL',
                        '3900  N SPRINGFIELD AVE, Chicago, IL',
                        '1700  N ASHLAND AVE, Chicago, IL',
                        '5100  W 72ND ST, Chicago, IL',
                        '5800  N RIDGE AVE, Chicago, IL',
                        '4200  W 65TH ST, Chicago, IL',
                        '7100  N HARLEM AVE, Chicago, IL',
                        '6200  N MCCLELLAN AVE, Chicago, IL',
                        '2900  W 85TH ST, Chicago, IL',
                        '3400  W 77TH ST, Chicago, IL',
                        '9600  S LONGWOOD DR, Chicago, IL',
                        '2100  N CANNON DR, Chicago, IL']

        ### Create 'Address' selection dropdown
        address_selected = st.selectbox('Select Address', address_options)

    ## 'Latitude'
    with col2:
        ### Create 'Latitude' sub-header
        st.subheader('Latitude')

        ### Create 'Latitude' options
        latitude_options = [41.95469, 41.994991, 41.974089, 41.9216, 41.891118, 41.867108, 41.896282,
                            41.919343, 41.921965, 41.688324, 41.862292, 41.720848, 41.731922, 41.891126,
                            41.999129, 42.01743, 41.907645, 41.732984, 41.981964, 41.944869, 42.011601,
                            41.94983, 41.979243, 41.986921, 41.801498, 41.906638, 41.723195, 41.868077,
                            41.869216, 41.662014, 41.961743, 41.953067, 41.878114, 41.958271, 41.932094,
                            41.994469, 42.006858, 41.916265, 41.846075, 41.918705, 41.682587, 41.725517,
                            41.948167, 41.963976, 41.953705, 41.964242, 41.990284, 42.008314, 41.991429,
                            41.843811, 41.921177, 41.852652, 41.857402, 41.868142, 41.846283, 41.721474,
                            41.869107, 41.719059, 41.966987, 41.923738, 41.970248, 42.010412, 41.89923,
                            41.692555, 41.94016, 41.903002, 41.942114, 41.960616, 41.883284, 41.704336,
                            41.962728, 41.836644, 41.837085, 41.911824, 41.823065, 41.801179, 41.800737,
                            41.778297, 41.77166, 41.759346, 41.768388, 41.797616, 41.781416, 41.773215,
                            41.822536, 41.799282, 41.794781, 41.778748, 41.766202, 41.754676, 41.821582,
                            41.803423, 41.754292, 41.798697, 41.776156, 41.82561, 41.673408, 41.726465,
                            41.678618, 41.737052, 41.740641, 41.680946, 41.686398, 41.729669, 41.704572,
                            41.74785, 41.775051, 41.644612, 41.733643, 41.717753, 41.750498, 41.702724,
                            41.984809, 41.772846, 41.825902, 41.659112, 41.992478, 41.974689, 41.957799,
                            41.925198, 41.973845, 41.743402, 41.728495, 41.947227, 41.793818, 41.753411,
                            41.904194, 41.951866, 41.912563, 41.763733, 41.98728, 41.776428, 42.009876,
                            41.994679, 41.738903, 41.753391, 41.71914, 41.925652]

        ### Create 'Latitude' selection dropdown
        latitude_selected = st.selectbox('Select Latitude', latitude_options)

    ## 'Longitude'
    with col3:
        ### Create 'Longitude' sub-header
        st.subheader('Longitude')

        ### Create 'Longitude' options
        longitude_options = [-87.800991, -87.769279, -87.824812, -87.666455, -87.654491, -87.654224,
                             -87.655232, -87.694259, -87.632085, -87.676709, -87.64886, -87.666014,
                            -87.677512, -87.61156, -87.795585, -87.687769, -87.760886, -87.649642,
                            -87.812827, -87.832763, -87.811506, -87.698457, -87.750938, -87.689778,
                            -87.763416, -87.701431, -87.64997, -87.666901, -87.627561, -87.724608,
                            -87.76007, -87.776792, -87.629798, -87.702575, -87.700117, -87.667736,
                            -87.675919, -87.800515, -87.716277, -87.752329, -87.707973, -87.614258,
                            -87.730698, -87.69181, -87.733974, -87.757639, -87.797127, -87.777921,
                            -87.747113, -87.686763, -87.79518, -87.719887, -87.694991, -87.696269,
                            -87.656913, -87.648064, -87.696293, -87.675088, -87.674677, -87.785288,
                            -87.787992, -87.66214, -87.716788, -87.598865, -87.794896, -87.688267,
                            -87.776385, -87.777189, -87.705085, -87.703736, -87.748367, -87.677737,
                            -87.729384, -87.726737, -87.678378, -87.679447, -87.71188, -87.752411,
                            -87.703047, -87.745602, -87.678649, -87.797894, -87.776532, -87.60088,
                            -87.666343, -87.585487, -87.615989, -87.586427, -87.562889, -87.612922,
                            -87.627796, -87.642984, -87.590773, -87.736812, -87.778927, -87.726549,
                            -87.599862, -87.585413, -87.559308, -87.543067, -87.546587, -87.535198,
                            -87.531635, -87.582699, -87.565666, -87.702716, -87.655356, -87.604498,
                            -87.55551, -87.531657, -87.605294, -87.536497, -87.728492, -87.740029,
                            -87.667827, -87.538693, -87.862995, -87.890615, -87.930995, -87.746381,
                            -87.805059, -87.731435, -87.600963, -87.671457, -87.654234, -87.639817,
                            -87.756155, -87.725057, -87.668055, -87.742302, -87.666066, -87.627096,
                            -87.807277, -87.770899, -87.695443, -87.707394, -87.669539, -87.63359]

        ### Create 'Longitude' selection dropdown
        longitude_selected = st.selectbox('Select Longitude', longitude_options)


    #### --- WEATHER --- ###
    ## Create 'Weather' header
    st.header('Weather')

    ## Create columns
    col1, col2, col3, col4 = st.columns(4)

    ## 'Temperature'
    with col1:
        ### Create 'Temperature' sub-header
        st.subheader('Temp (F)')

        ### Create 'Temperature' options
        #temperature_options = ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45', 
                        #'46', '47', '48', '49', '50', '51', '52', '53', '54', '55', 
                        #'56', '57', '58', '59', '60', '61', '62', '63', '64', '65', 
                        #'66', '67', '68', '69', '70', '71', '72', '73', '74', '75', 
                        #'76', '77', '78', '79', '80', '81', '82', '83', '84', '85', 
                        #'86', '87', '88', '89', '90', '91', '92', '93', '94']
        
        ### Create 'Temperature' selection dropdown
        #temperature_selected = st.selectbox('Select Temperature', temperature_options)
        ### Create 'Temperature' selection slider
        temperature_selected = st.slider(
        'Select temperature:',
        min_value=35, max_value=95, value=35, step=1)

    ## 'Humidity'
    with col2:
        ### Create 'Humidity' sub-header
        st.subheader('Humidity')

        ### Create 'Humidity' options
        #humidity_options = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
                        #32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 
                        #42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 
                        #52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 
                        #62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 
                        #72, 73, 74, 75]
        
        ### Create 'Humidity' selection dropdown
        #humidity_selected = st.selectbox('Select Humidity', humidity_options)
        ### Create 'Air Pressure' selection slider
        humidity_selected = st.slider(
        'Select humidity:',
        min_value=20, max_value=80, value=20, step=1)

    ## 'Air Pressure'
    with col3:
        ### Create 'Air Pressure' sub-header
        st.subheader('Air Pressure')

        ### Create 'Air Pressure' options
        #air_pressure_options = ['29.23', '29.25', '29.34', '29.43', '29.44', '29.45', '29.46', '29.47', '29.48', '29.50', 
                            #'29.51', '29.52', '29.53', '29.54', '29.55', '29.56', '29.59', '29.60', '29.61', '29.62', 
                            #'29.63', '29.64', '29.65', '29.66', '29.67', '29.68', '29.69', '29.70', '29.71', '29.72', 
                            #'29.73', '29.74', '29.75', '29.76', '29.77', '29.78', '29.79', '29.80', '29.81', '29.82', 
                            #'29.83', '29.84', '29.85', '29.86', '29.87', '29.88', '29.89', '29.90', '29.91', '29.92', 
                            #'29.93', '29.94', '29.95', '29.96', '29.97', '29.98', '29.99', '30.00', '30.01', '30.02', 
                            #'30.03', '30.04', '30.05', '30.06', '30.07', '30.08', '30.09', '30.10', '30.11', '30.12', 
                            #'30.13', '30.14', '30.15', '30.16', '30.17', '30.18', '30.19', '30.20', '30.21', '30.22', 
                            #'30.23', '30.24', '30.25', '30.26', '30.27', '30.28', '30.29', '30.30', '30.31', '30.32', 
                            #'30.33', '30.34', '30.35', '30.36', '30.37', '30.38', '30.39', '30.40', '30.41', '30.52', '30.53']
        
        ### Create 'Air Pressure' selection dropdown
        #air_pressure_selected = st.selectbox('Select Air Pressure', air_pressure_options)

        ### Create 'Air Pressure' selection slider
        air_pressure_selected = st.slider(
        'Select air pressure:',
        min_value=29.00, max_value=30.60, value=29.00, step=0.01)

    ## 'Wind Speed'
    with col4:
        ### Create 'Wind Speed' sub-header
        st.subheader('Wind Speed')

        ### Create 'Wind Speed' options
        #wind_speed_options = ['1.7', '1.9', '10.0', '10.1', '10.2', '10.3', '10.4', '10.5', '10.6', '10.7', 
                        #'10.8', '10.9', '11.0', '11.1', '11.2', '11.3', '11.4', '11.5', '11.6', '11.7', 
                        #'11.8', '11.9', '12.0', '12.1', '12.2', '12.3', '12.4', '12.5', '12.6', '12.7', 
                        #'12.8', '12.9', '13.0', '13.1', '13.2', '13.3', '13.4', '13.5', '13.6', '13.7', 
                        #'13.8', '13.9', '14.0', '14.1', '14.2', '14.3', '14.4', '14.5', '14.6', '14.7', 
                        #'14.8', '14.9', '15.0', '15.1', '15.2', '15.3', '15.4', '15.5', '15.6', '15.7', 
                        #'15.8', '15.9', '16.0', '16.1', '16.2', '16.3', '16.4', '16.6', '16.7', '16.8', 
                        #'16.9', '17.1', '17.2', '17.3', '17.4', '17.6', '17.7', '17.8', '17.9', '18.0', 
                        #'18.1', '18.2', '18.4', '18.5', '18.8', '18.9', '19.3', '19.5', '19.9', '2.0', 
                        #'2.1', '2.3', '2.4', '2.6', '2.7', '2.8', '2.9', '20.2', '20.7', '21.4', '21.5', 
                        #'22.1', '22.6', '22.9', '23.1', '23.2', '26.3', '3.0', '3.1', '3.2', '3.3', '3.4', 
                        #'3.5', '3.6', '3.7', '3.8', '3.9', '4.0', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6', 
                        #'4.7', '4.8', '4.9', '5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8', 
                        #'5.9', '6.0', '6.1', '6.2', '6.3', '6.4', '6.5', '6.6', '6.7', '6.8', '6.9', '7.0', 
                        #'7.1', '7.2', '7.3', '7.4', '7.5', '7.6', '7.7', '7.8', '7.9', '8.0', '8.1', '8.2', 
                        #'8.3', '8.4', '8.5', '8.6']
        
        ### Create 'Wind Speed' selection dropdown
        #wind_speed_selected = st.selectbox('Select Wind Speed', wind_speed_options)
        ### Create 'Wind Speed' selection slider
        wind_speed_selected = st.slider(
        'Select wind speed:',
        min_value=1.5, max_value=20.0, value=1.5, step=0.1)

if selected == 'Control Measures':

    ### --- PREVENTIVE MEASURES --- ###
    st.title('Control Measures')
    style = "<div style='background-color:#2C78DA; padding:2px'></div>"
    st.markdown(style, unsafe_allow_html = True)

    # Text
    st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>To monitor and control mosquito breeding, the City of Chicago has strategically applied the use of larvicide and adulticide in high-risk areas, as well as the deployment of specialized traps. This comprehensive approach by the city aims to ensure the well-being of its residents by mitigating the risk of the West Nile Virus.</span>", unsafe_allow_html=True) 
    st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>Zoom into the map below for the specific **spray (in green)** and **trap (in blue)** locations:</span>", unsafe_allow_html=True)
    st.markdown("")

    # Call 'spray_and_trap_locations' function and display the map
    map = spray_and_trap_locations(train_df, spray_df)
    map.save("my_map.html")
    with open("my_map.html") as f:
        map_html = f.read()

    html_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
        {map_html}
    </div>
    """
    st.components.v1.html(html_code, width=1000, height=700)


if selected == 'Contact Us':

    ### --- CONTACT US --- ###
    st.title('Contact Us')
    style = "<div style='background-color:#2C78DA; padding:2px'></div>"
    st.markdown(style, unsafe_allow_html = True)

    # Text
    st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>If you believe you may be at risk of West Nile virus or have questions about this infectious disease, don't hesitate to reach out for assistance and guidance. The City of Chicago and the Chicago Department of Public Health are here to support you and provide valuable information. </span>", unsafe_allow_html=True) 
    st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>We encourage you to contact us through the following means:</span>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")

    # Contact Information
    st.header("City of Chicago")
    
    ## Create columns
    col1, col2 = st.columns(2)

    with col1:

        # Contact of the City of Chicago
        st.subheader("Phone:")
        st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>**WNV Concerns:** 312.744.5000</span>", unsafe_allow_html=True)
        st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>**WNV Information:** 312.747.9884</span>", unsafe_allow_html=True)
        
        st.subheader("Email:")
        st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>healthychicago@cityofchicago.org</span>", unsafe_allow_html=True) 
        #st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>healthychicago@cityofchicago.org</span>", unsafe_allow_html=True)

    with col2:
        st.subheader("Address:")
        st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>City Hall, 121 N. LaSalle Street, Chicago, Illinois 60602</span>", unsafe_allow_html=True)        
        
        st.subheader("Website:")
        st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>https://www.chicago.gov/city/en.html</span>", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    st.markdown("")

    # Final text
    st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>Your health and well-being are of paramount importance to us. Please do not hesitate to get in touch if you have any questions, concerns, or require further guidance regarding West Nile virus prevention and management. We are here to help you stay safe and informed.</span>", unsafe_allow_html=True)    
        
        #st.write("<span style='font-size: 18px; font-family: Arial, sans-serif;'>https://www.chicago.gov/city/en.html</span>", unsafe_allow_html=True)
            #"Chicago Department of Public Health - West Nile Virus Information:\n"
            #"Address:" 
            #" - City Hall, 121 N. LaSalle Street, Chicago, Illinois 60602\n"
            #"Phone: 312.747.9884\n"
            #"Website: CDPH West Nile Virus Information\n\n"
            #"Your health and well-being are of paramount importance to us. Please do not hesitate to get in touch if you have any questions, concerns, or require further guidance regarding West Nile virus prevention and management. We are here to help you stay safe and informed."
            #"</span>", unsafe_allow_html=True
            #)
    

    #st.write("<span style='font-size: 24px; font-family: Arial, sans-serif;'>Hello, how are you?</span>", unsafe_allow_html=True)