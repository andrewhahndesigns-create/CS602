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
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os
import streamlit as st


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

#################################################
#################################################
elif page == 'Near Earth Objects':
    st.header("Near Earth Objects \"Asteroids\"")

    # ----------------------------
    # 1. Load saved NASA NEO JSON & CREATE DATAFRAME. Rows = Asteroid | Columns = Atrributes
    # ----------------------------

    # Get folder where your script lives
    base_dir = os.path.dirname(__file__)

    # Build full path to the JSON file
    file_path = os.path.join(base_dir, "neo_browse_data.json")

    # Open the file using the full path
    r_file = open(file_path, "r")

    # Load JSON into Python dictionary
    neo_resp = json.load(r_file)

    # Close the file manually
    r_file.close()

    asteroids = neo_resp["near_earth_objects"]

    # Convert list of asteroid dictionaries into a DataFrame
    df = pd.json_normalize(asteroids)

    # # display all columns with .head()
    # pd.set_option('display.max_columns', None)
    # print(df.head())

    # ----------------------------
    # 2. [VIZ1] BAR CHART (SIZE DISTRIBUTION of Max Estimated Miles DIAMETER)
    # ----------------------------

    st.header("Estimated Asteroid Size Distribution")

    # Define bins (ranges)
    bins = [0, 10, 20, 30, 40, 50, 60]

    # [DA7] & [DA9] create new column/group column, Add new column or perform calculations on DataFrame columns
    # Create a new column grouping asteroid sizes into ranges
    df["size_range"] = pd.cut(
        df["estimated_diameter.miles.estimated_diameter_max"],
        bins=bins,
        labels=["0-10", "10-20", "20-30", "30-40", "40-50", "50-60"]
    )

    # pd.set_option('display.max_rows', None)  # show all rows
    # print(
    #     df[[
    #         "estimated_diameter.miles.estimated_diameter_max",
    #         "size_range"
    #     ]]
    # )

    # Count how many asteroids fall into each range as a Series
    # [DA2] sort data .sort_index()
    size_counts = df["size_range"].value_counts().sort_index()

    # Create figure
    fig2, ax2 = plt.subplots()

    # Plot bar chart
    size_counts.plot(
        kind="bar",
        title="Asteroid Size Distribution",
        ax=ax2
    )

    # Label axes
    ax2.set_xlabel("Diameter (miles)")
    ax2.set_ylabel("Number of Asteroids")

    # Rotate labels so they fit better
    ax2.tick_params(axis="x", rotation=45)

    # Show in Streamlit
    st.pyplot(fig2)

    # ----------------------------
    # 3. [VIZ2] PIE CHART (HAZARDOUS VS NOT)
    # ----------------------------

    st.header("Potentially Hazardous Asteroids")

    # Count how many True vs False values
    # True = hazardous
    # False = not hazardous
    haz_counts = df["is_potentially_hazardous_asteroid"].value_counts()

    # Create a figure (canvas) and axis (drawing area)
    fig1, ax1 = plt.subplots()

    # Plot pie chart
    haz_counts.plot(
        kind="pie",  # pie chart
        autopct="%1.1f%%",  # show percentages
        ylabel="",  # remove default label
        title="Hazardous vs Not Hazardous",
        ax=ax1  # draw on this axis
    )

    # Display chart in Streamlit
    st.pyplot(fig1)

    # ----------------------------
    # 4a. CREATE CLOSE-APPROACH DATAFRAME
    # ----------------------------

    # This extracts nested data (each asteroid has MANY approach records)
    approach_df = pd.json_normalize(
        asteroids,
        record_path="close_approach_data",  # list inside each asteroid
        meta=["id", "name_limited", "is_potentially_hazardous_asteroid"]
    )

    # Convert string dates → real datetime objects
    approach_df["close_approach_date"] = pd.to_datetime(
        approach_df["close_approach_date"]
    )

    # ----------------------------
    # 4b. USER INPUT (SLIDER)
    # ----------------------------

    st.header("Hazardous Asteroid Close Approaches")
    # [ST1] Streamlit Slider widget
    # Slider lets user choose number of years
    years_to_scan = st.slider(
        "Select number of years into the future:",
        min_value=5,  # minimum allowed
        max_value=40,  # maximum allowed
        value=10  # default value
    )

    # Get today's date
    today = pd.Timestamp(date.today())

    # Calculate future cutoff date based on slider
    future_end_date = today + pd.DateOffset(years=years_to_scan)

    # ----------------------------
    # 4c. FILTER DATA
    # ----------------------------

    # Keep only:
    # - hazardous asteroids
    # - dates between today and future_end_date
    future_hazardous = approach_df[
        (approach_df["is_potentially_hazardous_asteroid"] == True) &
        (approach_df["close_approach_date"] >= today) &
        (approach_df["close_approach_date"] <= future_end_date)
        ].copy()

    # Extract year (for x-axis)
    future_hazardous["year"] = future_hazardous["close_approach_date"].dt.year

    # Create y-values (counts per year)
    # groupby groups rows by year
    # cumcount counts 0,1,2... within each year
    # +1 makes it start at 1 instead of 0
    future_hazardous["y"] = future_hazardous.groupby("year").cumcount() + 1

    # ----------------------------
    # 4d. [VIZ3] SCATTER PLOT
    # ----------------------------

    fig3, ax3 = plt.subplots(figsize=(10, 6))

    # Plot points
    ax3.scatter(
        future_hazardous["year"],  # x = year
        future_hazardous["y"]  # y = count
    )

    # Add labels (asteroid names)
    for _, row in future_hazardous.iterrows():
        ax3.text(
            row["year"],
            row["y"],
            row["name_limited"],
            fontsize=8
        )

    # Axis labels and title
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Number of Hazardous Asteroids")
    ax3.set_title(f"Hazardous Asteroid Approaches (Next {years_to_scan} Years)")

    # Show all years on x-axis
    ax3.set_xticks(range(today.year, today.year + years_to_scan + 1))

    # Limit y-axis to 0–5
    ax3.set_yticks(range(0, 6))
    ax3.set_ylim(0, 3)

    fig3.tight_layout()

    # Show chart in Streamlit
    st.pyplot(fig3)

#################################################
#################################################
elif page == 'Earth Observatory Natural Event Tracker':
    st.header("Earth Observatory Natural Event Tracker")
