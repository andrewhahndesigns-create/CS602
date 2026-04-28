"""
GROUP 1: Andrew Hanh and Samantha Osborne
DATA: We worked with 2 datasets from NASA:
    -- Near Earth Object (Asteroids)
    -- Natural Event Observational Data.

DESCRIPTION:
   Our Web App has three 'pages,' which one can explore from the radio sidebar options. 
   
   The landing page displays an image that changes daily (from NASA's 'Picture of the Day') API. 
   We Cache the API reponse for one day after being called to display the image and caption using the st.image()

   Then we have two data-driven pages, each deriving their data from JSON datasets that we retreived once 
   and stored. The first dataset provides data on asteroids from NASA's Asteroid team. The second datset provides 
   information on Natural Events observed in NASA imagery. 

"""


import requests
import streamlit as st
import pandas as pd
import json

############### [ST4] Setting the background & Sidebar Radio Buttons
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#######
st.sidebar.title("Welcome")
sidebar_options = ['Astronomy Picture of the Day','Near Earth Objects','Earth Observatory Natural Event Tracker']
page = st.sidebar.radio("Explore NASA Data", sidebar_options)

#################################################
if page == 'Astronomy Picture of the Day':
    st.header("Astronomy Picture of The Day")

    # function decorator; Wrap this function with Streamlit’s caching system
    @st.cache_data(ttl=86400)
    def get_apod():
        API_KEY = "DEMO_KEY"
        url = "https://api.nasa.gov/planetary/apod"


        params = {
            "api_key": API_KEY
        }
        # requests.get() accepts params argument that takes a dictionary and append it to the url sent out.
        response = requests.get(url, params=params)

        # print(response.json())
        apod_resp = response.json()
        return apod_resp


    apod_response = get_apod()
    # print(apod_response)
    st.image(apod_response['url'], caption=f'{apod_response['date']} : {apod_response['explanation']}')


elif page == 'Near Earth Objects':
    st.header("Near Earth Objects \"Asteroids\"")


elif page == 'Earth Observatory Natural Event Tracker':
    st.header("Earth Observatory Natural Event Tracker")
