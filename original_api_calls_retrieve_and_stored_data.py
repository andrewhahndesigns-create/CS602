
# https://api.nasa.gov/
'''
NASA offers numerous free APIs, however, there is a rate limit of 50 requests per IP per day
for the Demo Key. Group 1 decided to write a function to call our two main APIs, and then store the JSON
repsonse packet in a file, so we could use that to query from for our streamlit web-application

Upon calling both APIs the Eonet API was discovered to have a limit on its call of data of roughly ~6500 events
of which were mostly wildfires, inorder to get a more even spread of data the def get_api_response was split
so that Eonet could set categories and limits per category.
'''
import requests


# [PY1] A function with two or more parameters,
# one of which has a default value, called at least twice (once with the default value and once without)

# Function to call api with default api-key and write response JSON to a file
def get_api_response(url, json_file_name, api_key = "DEMO_KEY"):
    import requests
    import json

    params = {
        "api_key": api_key
    }

    # requests.get() accepts params argument that takes a dictionary and append it to the url sent out.
    response = requests.get(url, params=params)

    # [PY5] A dictionary where you write code to access its keys, values, or items
    resp = response.json() # response is string in JSON format, .json() converts it to a python dictionary
    print(response.json())

    w_file = open(json_file_name, "w")  # w- write
    json.dump(resp, w_file, indent=2)  # write JSON
    w_file.close()


# Ran once for Near Earth Object 'Browse' Data
get_api_response("https://api.nasa.gov/neo/rest/v1/neo/browse", "neo_browse_data.json")


# Ran once for Near Earth Object 'Browse' Data

import requests
import json

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

with open("natural_events_data.json", "w") as f:
    json.dump({"events": all_events}, f, indent=2)

print(f"Saved {len(all_events)} events to natural_events_data.json")


