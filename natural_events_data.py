import math
import datetime
import requests
import pandas as pd
import streamlit as st
import json
import pydeck as pdk  # [VIZ 4 MAP] Extra credit - interactive map
from geopy.geocoders import Nominatim


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


def haversine_km(lat1, lon1, lat2, lon2):
    radius_earth_km = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth_km * c


def get_latest_geometry(event):
    geometry = event.get("geometry", [])

    if not geometry:
        return None

    return geometry[-1]


# [PY1] Function with two parameters, one with a default value (distance_km=None)
# Called without distance_km in parse_events(), and with it in filter_by_location()
def score_relevance(category, distance_km=None):
    # [PY5] Dictionary accessed with .get() to look up category weight values
    category_weights = {
        "Wildfires": 3,
        "Severe Storms": 3,
        "Volcanoes": 3,
        "Floods": 3,
        "Landslides": 3,
        "Dust and Haze": 2,
        "Temperature Extremes": 2,
        "Sea and Lake Ice": 1,
        "Snow": 1,
        "Water Color": 1,
    }

    base = category_weights.get(category, 1)

    if distance_km is None:
        total = base
    elif distance_km <= 50:
        total = base + 3
    elif distance_km <= 150:
        total = base + 2
    elif distance_km <= 300:
        total = base + 1
    else:
        total = base

    if total >= 5:
        return "High"
    elif total >= 3:
        return "Medium"
    return "Low"


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
            # [DA9] New column calculated from existing category data
            "relevance": score_relevance(category_title),
            "distance_km": None,
            "link": event.get("link")
        })

    return pd.DataFrame(rows)


def filter_by_location(df, user_lat, user_lon, radius_km):
    filtered = df.copy()

    # [DA9] Adding a new calculated column — distance from the user's location
    filtered["distance_km"] = filtered.apply(
        lambda row: haversine_km(
            user_lat,
            user_lon,
            row["latitude"],
            row["longitude"]
        ),
        axis=1
    )

    # [DA4] Filter data by one condition — keep only events within the radius
    filtered = filtered[filtered["distance_km"] <= radius_km].copy()
    filtered["distance_km"] = filtered["distance_km"].round(1)

    filtered["relevance"] = filtered.apply(
        lambda row: score_relevance(row["category"], row["distance_km"]),
        axis=1
    )

    # [DA2] Sort data in ascending order by distance from user location
    return filtered.sort_values(by="distance_km")


# ── Page setup ────────────────────────────────────────────────────────────────

# [ST4] Customized page design — wide layout, custom icon, sidebar navigation
st.set_page_config(
    page_title="EONET Global Event Map",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 NASA EONET Global Natural Event Map")
st.caption("Explore global natural events first, then filter by location.")


# ── Sidebar ───────────────────────────────────────────────────────────────────

# [ST4] Sidebar used as a structured filter/navigation panel
with st.sidebar:

    # ── Time filter ───────────────────────────────────────────────────────────

    st.header("Time Filter")

    # [ST1] Radio button widget
    time_mode = st.radio(
        "Filter by",
        ["Look back (days)", "Date range"],
        horizontal=True
    )

    if time_mode == "Look back (days)":
        # [ST2] Checkbox widget
        all_time = st.checkbox("All time", value=True)

        if all_time:
            days = None
        else:
            # [ST3] Slider widget
            days = st.slider(
                "Look back period",
                min_value=1,
                max_value=365,
                value=365
            )

        start_date = None
        end_date = None

    else:
        # [ST2] Date input widget — calendar-based range picker
        date_range = st.date_input(
            "Select date range",
            value=(
                datetime.date.today() - datetime.timedelta(days=30),
                datetime.date.today()
            ),
            min_value=datetime.date(2015, 1, 1),
            max_value=datetime.date.today()
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            st.info("Please select both a start and end date.")
            st.stop()

        days = None

    # ── Location search ───────────────────────────────────────────────────────

    st.header("Location Search")

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

    # ── Category toggles ──────────────────────────────────────────────────────

    st.header("Event Categories")

    col_a, col_b = st.columns(2)

    select_all = col_a.button("Select all", use_container_width=True)
    clear_all = col_b.button("Clear all", use_container_width=True)

    for label in CATEGORY_OPTIONS:
        key = f"cat_{label}"
        if key not in st.session_state:
            st.session_state[key] = True

    if select_all:
        for label in CATEGORY_OPTIONS:
            st.session_state[f"cat_{label}"] = True

    if clear_all:
        for label in CATEGORY_OPTIONS:
            st.session_state[f"cat_{label}"] = False

    # [ST2] Checkbox widgets — one rendered per category
    selected_labels = []
    for label in CATEGORY_OPTIONS:
        key = f"cat_{label}"
        checked = st.checkbox(label, value=st.session_state[key], key=key)
        if checked:
            selected_labels.append(label)

    # [PY4] List comprehension — translates selected labels into API slugs
    selected_slugs = [CATEGORY_OPTIONS[label] for label in selected_labels]

    if not selected_labels:
        st.warning("Select at least one category.")
        st.stop()

    st.divider()


# ── Main content ──────────────────────────────────────────────────────────────

# [PY3] Error checking with try/except — catches NASA API failures gracefully
try:
    with st.spinner("Loading events..."):
        with open("natural_events_data.json", "r") as f:
            data = json.load(f)
        all_events = data.get("events", [])

        # Filter by selected categories, then apply a per-category cap
        # (mirrors the limit=1000 per-category behavior of the live API version)
        selected_titles = set(selected_labels)
        PER_CATEGORY_LIMIT = 1000

        category_counts = {}
        capped_events = []

        for e in all_events:
            event_cats = [c["title"] for c in e.get("categories", []) if c["title"] in selected_titles]
            if not event_cats:
                continue
            cat = event_cats[0]
            if category_counts.get(cat, 0) < PER_CATEGORY_LIMIT:
                capped_events.append(e)
                category_counts[cat] = category_counts.get(cat, 0) + 1

        events = capped_events if selected_labels else all_events[:PER_CATEGORY_LIMIT * len(CATEGORY_OPTIONS)]

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

    # ── Metrics ───────────────────────────────────────────────────────────────

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
        opacity=0.75,
        stroked=True,
        filled=True,
    )

    layers = [event_layer]

    if user_lat is not None and user_lon is not None:
        user_df = pd.DataFrame([{
            "latitude": user_lat,
            "longitude": user_lon,
            "title": location_input,
            "category": "Search Location",
            "date": "",
            "distance_km": "",
            "relevance": ""
        }])

        user_layer = pdk.Layer(
            "ScatterplotLayer",
            data=user_df,
            get_position="[longitude, latitude]",
            get_radius=80000,
            get_fill_color=[0, 180, 255, 220],
            pickable=True,
            stroked=True,
            filled=True,
        )

        layers.append(user_layer)

        view_state = pdk.ViewState(
            latitude=user_lat,
            longitude=user_lon,
            zoom=4,
            pitch=0,
        )
    else:
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
                "text": "{title}\nCategory: {category}\nDate: {date}\nDistance: {distance_km} km\nRelevance: {relevance}"
            }
        ),
        use_container_width=True
    )

    # ── Events Table ──────────────────────────────────────────────────────────

    st.subheader("Events")

    # [DA2] Sort data in ascending or descending order by the selected column
    sort_option = st.selectbox(
        "Sort by",
        ["date", "category", "relevance", "distance_km"]
    )

    if sort_option in display_df.columns:
        display_df = display_df.sort_values(by=sort_option, na_position="last")

    # [DA7] Select specific columns to display, dropping unused ones
    cols = ["title", "category", "date", "relevance", "latitude", "longitude"]

    if display_df["distance_km"].notna().any():
        cols.append("distance_km")

    # [DA3] Top values shown first based on sort — e.g. most recent or closest
    st.dataframe(
        display_df[cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "title":       st.column_config.TextColumn("Event"),
            "category":    st.column_config.TextColumn("Category"),
            "date":        st.column_config.TextColumn("Date"),
            "relevance":   st.column_config.TextColumn("Relevance"),
            "latitude":    st.column_config.NumberColumn("Lat", format="%.4f"),
            "longitude":   st.column_config.NumberColumn("Lon", format="%.4f"),
            "distance_km": st.column_config.NumberColumn("Distance (km)", format="%.1f"),
        }
    )

except FileNotFoundError:
    st.error("Could not find natural_events_data.json — make sure the file is in the same folder as your script.")