
# https://api.nasa.gov/
'''
NASA offers numerous free APIs, however, there is a rate limit of 50 requests per IP per day
for the Demo Key. Group 1 decided to write a function to call our two main APIs, and then store the JSON
repsonse packet in a file, so we could use that to query from for our streamlit web-application.
'''

import requests
import json

# [PY1]
# Function to call API and write response JSON to a file
def get_api_response(url, json_file_name, api_key="DEMO_KEY"):

    all_neos = []

    # loop through pages (adjust range as needed)
    for page in range(0, 9):  # ~20 per page → about 180 asteroids total
        params = {
            "api_key": api_key,
            "page": page
        }

        response = requests.get(url, params=params)
        #Convert API response to Python data
        resp = response.json()

        print(f"Fetched page {page}")

         # pull only the array
        neos = resp.get("near_earth_objects", [])
        all_neos.extend(neos)


    w_file = open(json_file_name, "w")
    # Save big list as JSON: json.dump(data, file). You are creating one top-level JSON object (a dict) with a single key
    json.dump({"near_earth_objects": all_neos}, w_file)
    w_file.close()

    print(f"Saved {len(all_neos)} asteroids to {json_file_name}")

# Ran once for Near Earth Object 'Browse' Data
get_api_response("https://api.nasa.gov/neo/rest/v1/neo/browse", "neo_browse_data.json")





# New code for Eonet pull
'''
The Eonet API has a limit on its call of data of roughly ~6500 events
of which were mostly wildfires, inorder to get a more even spread of data the def get_api_response was split
so that Eonet could set categories and limits per category.
'''

EONET_CATEGORIES = [
    "wildfires", "severeStorms", "volcanoes", "floods",
    "landslides", "snow", "dustHaze", "seaLakeIce",
    "waterColor", "tempExtremes"
]

seen_ids = set()
all_events = []

for slug in EONET_CATEGORIES:
    params = {"status": "all", "limit": 1000, "category": slug}
    response = requests.get("https://eonet.gsfc.nasa.gov/api/v3/events", params=params)
    events = response.json().get("events", [])
    for event in events:
        if event["id"] not in seen_ids:
            seen_ids.add(event["id"])
            all_events.append(event)


w_file = open("natural_events_data.json", "w")
json.dump({"events": all_events}, w_file)
w_file.close()

print(f"Saved {len(all_events)} events to natural_events_data.json")
