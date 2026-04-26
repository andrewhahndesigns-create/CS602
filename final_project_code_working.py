import requests
import streamlit as st
import pandas as pd

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
