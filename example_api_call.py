import requests

# Example query
# https://api.nasa.gov/neo/rest/v1/neo/browse?api_key=DEMO_KEY

url = "https://api.nasa.gov/neo/rest/v1/neo/browse"
params = {
    "api_key": "DEMO_KEY"
}

# requests.get() accepts params argument that takes a dictionary and append it to the url sent out.
response = requests.get(url, params=params)

resp = response.json()  # response is string in JSON format, .json() converts it to a python dictionary
print(response.json())
