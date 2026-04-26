# import requests
# import json

# """
# # Browse the overall Asteroid data-set
# API_KEY = "DEMO_KEY"
# url = "https://api.nasa.gov/neo/rest/v1/neo/browse"
# params = {
#     "api_key": API_KEY
# }
# # requests.get() accepts params argument that takes a dictionary and append it to the url sent out.
# response = requests.get(url, params=params)
# print(response.json())
# neo_resp = response.json()

# w_file = open("neo_browse_data.json", "w")  # w- write
# json.dump(neo_resp, w_file, indent=2)  # write JSON
# w_file.close() 
# """




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

    resp = response.json()
    print(response.json())

    w_file = open(json_file_name, "w")  # w- write
    json.dump(resp, w_file, indent=2)  # write JSON
    w_file.close()


# Ran once for Near Earth Object 'Browse' Data
get_api_response("https://api.nasa.gov/neo/rest/v1/neo/browse", "neo_browse_data.json", "DEMO_KEY")


# And ran again for Natural Event Tracker Data
