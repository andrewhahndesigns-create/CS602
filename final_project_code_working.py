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



import math
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime 
import os
import streamlit as st
import pydeck as pdk  # [VIZ 4 MAP] Extra credit - interactive map
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


############### [ST4] Setting the background & Sidebar Radio Buttons
st.set_page_config(
    page_title="NASA Data",
    page_icon="🌎",
    layout="wide"
)


#######
st.sidebar.title("Welcome")
sidebar_options = ['Astronomy Picture of the Day','Near Earth Objects','Earth Observatory Natural Event Tracker']
page = st.sidebar.radio("Explore NASA Data", sidebar_options)

#################################################
#################################################
# page = 'Near Earth Objects'
# page = 'Earth Observatory Natural Event Tracker'

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


    st.set_page_config(
        layout="centered"
    )

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

    # df.info()

    # # display all columns with .head()
    # pd.set_option('display.max_columns', None)
    # print(df.head())

    # ----------------------------
    # 2. [VIZ1] BAR CHART (SIZE DISTRIBUTION of Max Estimated Miles DIAMETER)
    # ----------------------------

    st.header("Distribution of Estimated Asteroid Size (Diameter in Miles)")

    # print(df["estimated_diameter.miles.estimated_diameter_max"].max())

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
    # size_counts is a series
    size_counts = df["size_range"].value_counts().sort_index()

    st.bar_chart(size_counts)

    # ----------------------------
    # 3. [VIZ2] PIE CHART (HAZARDOUS VS NOT)
    # ----------------------------

    st.header("Hazardous vs Not Hazardous Asteroids")

    haz_counts = df["is_potentially_hazardous_asteroid"].value_counts()
    # haz_counts = df["is_sentry_object"].value_counts()

    # Create a figure (canvas) and axis (drawing area)
    fig1, ax1 = plt.subplots(figsize=(4,4))

    # Plot pie chart
    haz_counts.plot(
        kind="pie",  # pie chart
        autopct="%1.1f%%",  # show percentages
        ylabel="",  # remove default label
        ax=ax1  # draw on this axis
    )

    # Display chart in Streamlit
    st.pyplot(fig1,use_container_width=False)

    # ----------------------------
    # 4a. CREATE CLOSE-APPROACH DATAFRAME
    # ----------------------------

    # This extracts nested data (each asteroid has MANY approach records)
    approach_df = pd.json_normalize(
        asteroids,
        record_path="close_approach_data",  # list inside each asteroid
        meta=["id", "name", "is_potentially_hazardous_asteroid"]
    )
    # You now get 1 row per approach event in the approach_df dataframe

    # Convert string dates → real datetime objects
    approach_df["close_approach_date"] = pd.to_datetime(
        approach_df["close_approach_date"]
    )

    # ----------------------------
    # 4b. USER INPUT (SLIDER)
    # ----------------------------

    st.header("Number of Hazardous Asteroids with a 'Close Approach' by Year")
    # [ST1] Streamlit Slider widget
    # Slider lets user choose number of years
    years_to_scan = st.slider(
        "Select number of years into the future you wish to see on the line chart:",
        min_value=5,  # minimum allowed
        max_value=30,  # maximum allowed
        value=10  # default value
    )

    # Get today's date
    today = pd.Timestamp(datetime.date.today())

    # years_to_scan=30

    # Calculate future cutoff date based on slider
    future_end_date = today + pd.DateOffset(years=years_to_scan)


    # ----------------------------
    # 4c. PREP DATA FOR LINE CHART
    # ----------------------------

    # FILTER DATA

    future_hazardous = approach_df[
        (approach_df["is_potentially_hazardous_asteroid"] == True) &
        (approach_df["close_approach_date"] >= today) &
        (approach_df["close_approach_date"] <= future_end_date)
        ]

    # Extract year (for grouping)
    future_hazardous["year"] = future_hazardous["close_approach_date"].dt.year

    # Count number of hazardous asteroids per year as a Series
    year_counts = future_hazardous["year"].value_counts().sort_index()

    # print(year_counts)

    # ----------------------------
    # 4d. [VIZ3] LINE CHART
    # ----------------------------

    # Convert index to string
    year_counts.index = year_counts.index.astype(str)

    st.line_chart(year_counts)

#################################################
#################################################
elif page == 'Earth Observatory Natural Event Tracker':
    st.header("Earth Observatory Natural Event Tracker")

    # [PY5] Dictionary - maps category names to their EONET API slugs,
    # accessed throughout the code using keys and values
    CATEGORY_OPTIONS = {
    "Wildfires": "wildfires",
    "Severe Storms": "severeStorms",
    "Volcanoes": "volcanoes",
    "Floods": "floods",
    "Landslides": "landslides",
    "Snow": "snow",
    "Dust and Haze": "dustHaze",
    "Sea and Lake Ice": "seaLakeIce",
    "Water Color": "waterColor",
    "Temperature Extremes": "tempExtremes",
    }
    
    # [PY2] Function that returns more than one value (latitude AND longitude)
    def geocode_location(place_name):
        geolocator = Nominatim(user_agent="eonet_global_event_map")
        location = geolocator.geocode(place_name)
    
        if location is None:
            return None, None
    
        return location.latitude, location.longitude
    
    def get_latest_geometry(event):
        geometry = event.get("geometry", [])
    
        if not geometry:
            return None
    
        return geometry[-1]
    
    # [DA1] Cleans and manipulates raw NASA JSON into a structured DataFrame
    def parse_events(events):
        rows = []
    
        # [DA8] Iterating through every event row to extract and reshape data
        for event in events:
            latest_geometry = get_latest_geometry(event)
    
            if not latest_geometry:
                continue
    
            coords = latest_geometry.get("coordinates")
    
            if not coords or len(coords) < 2:
                continue
    
            lon, lat = coords[0], coords[1]
    
            categories = event.get("categories", [])
            category_title = categories[0]["title"] if categories else "Unknown"
    
            rows.append({
                "title": event.get("title"),
                "category": category_title,
                "date": latest_geometry.get("date", "Unknown"),
                "latitude": lat,
                "longitude": lon,
                "distance_km": None,
                "link": event.get("link")
            })
    
        return pd.DataFrame(rows)
    
    def filter_by_location(df, user_lat, user_lon, radius_km):
        filtered = df.copy()
    
        # [DA9] Adding a new calculated column — distance from the user's location
        distances = []
        for i in range(len(filtered)):
            row = filtered.iloc[i]
            dist = geodesic((user_lat, user_lon), (row["latitude"], row["longitude"])).km
            distances.append(dist)
        filtered["distance_km"] = distances
        filtered["distance_km"] = filtered["distance_km"].round(1)
    
        # [DA4] Filter data by one condition — keep only events within the radius
        filtered = filtered[filtered["distance_km"] <= radius_km]
    
        # [DA2] Sort data in ascending order by distance from user location
        return filtered.sort_values(by="distance_km")
    
    # ── Metrics placeholder — renders here, filled after data loads ───────────────
    metrics_container = st.container()
    
    st.divider()
    
    # ── Filters — one row, two sections ─────────────────────
    
    location_col, category_col = st.columns([1, 2], gap="large")
    
    # ── Location search ───────────────────────────────────────────────────────────
    
    with location_col:
        st.markdown("#### Location Search")
    
        # [ST3] Text input widget
        location_input = st.text_input(
            "Search near a location",
            placeholder="Example: Tokyo, Japan"
        )
    
        # [ST3] Slider widget
        radius_km = st.slider(
            "Radius around location (km)",
            min_value=50,
            max_value=3000,
            value=500,
            step=50
        )
    
        apply_location_filter = st.button("Search This Area")
    
    # ── Category toggles ──────────────────────────────────────────────────────────
    
    with category_col:
        st.markdown("#### Event Categories")
    
        selected_labels = []
        toggle_cols = st.columns(2)
        for i, label in enumerate(CATEGORY_OPTIONS):
            if toggle_cols[i % 2].toggle(label, value=True):
                selected_labels.append(label)
    
        selected_slugs = [CATEGORY_OPTIONS[label] for label in selected_labels]
    
        if not selected_labels:
            st.warning("Select at least one category.")
            st.stop()
    
    st.divider()
    
    # ── Load and display ──────────────────────────────────────────────────────────
    
    # [PY3] Error checking with try/except — catches file load failures gracefully
    try:
        with st.spinner("Loading events..."):
            basedir = os.path.dirname(__file__)
            file_path = os.path.join(basedir, "natural_events_data.json")
    
            r_file = open(file_path, "r")
            data_resp = json.load(r_file)
            r_file.close()
    
            all_events = data_resp.get("events", [])
    
            # Filter by selected categories
            selected_titles = set(selected_labels)
            events = [
                e for e in all_events
                if any(c["title"] in selected_titles for c in e.get("categories", []))
            ] if selected_labels else all_events
    
            df = parse_events(events)
    
        df = parse_events(events)
    
        if df.empty:
            st.info("No events found for the selected filters.")
            st.stop()
    
        display_df = df.copy()
        user_lat = None
        user_lon = None
    
        if apply_location_filter and location_input:
            # [PY2] geocode_location() returns two values — unpacked into lat and lon
            user_lat, user_lon = geocode_location(location_input)
    
            if user_lat is None:
                st.error("Could not find that location.")
                st.stop()
    
            display_df = filter_by_location(df, user_lat, user_lon, radius_km)
    
            if display_df.empty:
                st.info("No events found near that location.")
                st.stop()
    
            st.success(
                f"Showing {len(display_df)} events within {radius_km} km of {location_input}."
            )
    
        # ── Metrics — filled into the placeholder defined above the filters ───────
    
        with metrics_container:
            all_cols = st.columns(len(selected_labels) + 1)
            all_cols[0].metric("Total Events", len(display_df))
    
            for i, cat in enumerate(selected_labels):
                count = len(display_df[display_df["category"] == cat])
                all_cols[i + 1].metric(cat, count)
    
        # ── Map ───────────────────────────────────────────────────────────────────
    
        # [VIZ 4 MAP] Interactive geographic map — extra credit
        st.subheader("Global Event Map")
    
        event_layer = pdk.Layer(
            "ScatterplotLayer",
            data=display_df,
            get_position="[longitude, latitude]",
            get_radius=40000,
            get_fill_color=[255, 100, 100, 200],
            pickable=True,
            filled=True,
        )
    
        layers = [event_layer]
    
        view_state = pdk.ViewState(
            latitude=15,
            longitude=0,
             zoom=1.3,
             pitch=0,
        )
    
        st.pydeck_chart(
            pdk.Deck(
                initial_view_state=view_state,
                layers=layers,
                tooltip={
                    "text": "{title}\nCategory: {category}\nDate: {date}\nDistance: {distance_km} km"
                }
            ),
            use_container_width=True
        )
    
    except FileNotFoundError:
        st.error("Could not find natural_events_data.json — make sure the file is in the same folder as your script.")
