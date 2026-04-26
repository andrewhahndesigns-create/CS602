import requests
import json

"""
# Browse the overall Asteroid data-set
API_KEY = "DEMO_KEY"
url = "https://api.nasa.gov/neo/rest/v1/neo/browse"
params = {
    "api_key": API_KEY
}
# requests.get() accepts params argument that takes a dictionary and append it to the url sent out.
response = requests.get(url, params=params)
print(response.json())
neo_resp = response.json()

w_file = open("neo_browse_data.json", "w")  # w- write
json.dump(neo_resp, w_file, indent=2)  # write JSON
w_file.close() 
"""
