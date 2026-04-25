import requests

url = "https://eonet.gsfc.nasa.gov/api/v3/events"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")