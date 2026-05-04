# 1) Getting today's date from datetime
# 2) And flattening nested JSON using the pd.json_normalize() function


import pandas as pd
import os
import json
import datetime

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "neo_browse_data.json")
r_file = open(file_path, "r")

# Load JSON into Python dictionary
neo_resp = json.load(r_file)
r_file.close()

asteroids = neo_resp["near_earth_objects"]

# Convert list of asteroid dictionaries into a DataFrame
df = pd.json_normalize(asteroids)

df.info()

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

print()
print()
print()
pd.set_option('display.max_columns', None)
print(approach_df.head(2))

# Convert string dates → real datetime objects
approach_df["close_approach_date"] = pd.to_datetime(
    approach_df["close_approach_date"]
)


# ----------------------------
# 4b. USER INPUT (SLIDER)
# ----------------------------


#In real code, set by user streamlit slider
years_to_scan = 10


# Get today's date
today = pd.Timestamp(datetime.date.today())
print()
print()
print()
print('Today')
print(today)

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

print()
print()
print()
print(year_counts)
