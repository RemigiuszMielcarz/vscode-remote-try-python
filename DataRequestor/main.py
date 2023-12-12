import os
import requests
import time
from datetime import datetime

class WeatherRequester:
    def __init__(self, location):
        self.location = location
        self.api_url = "https://api.openaq.org/v2/latest"
        self.locations_url = "https://api.openaq.org/v2/locations"

    def get_location_id(self):
        params = {
            'city': self.location,
            'limit': 1
        }
        response = requests.get(self.locations_url, params=params)
        if response.status_code == 200 and response.json()['results']:
            print("Dokładniejsza lokalizacja: ", response.json()['results'][0]['name'])
            return response.json()['results'][0]['id']
        else:
            print("Failed to find location ID")
            return None

    def fetch_data(self, location_id):
        params = {
            'location_id': location_id
        }
        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data")
            return None

    def format_data(self, data):
        measurements = data['results'][0]['measurements']
        formatted_data = {
            "location": self.location,
            "timestamp": datetime.now().isoformat(),
            "values": measurements
        }
        return formatted_data

    def print_data(self, location_id):
        data = self.fetch_data(location_id)
        if data:
            formatted_data = self.format_data(data)
            print(formatted_data)

if __name__ == "__main__":
    location = os.getenv("LOCATION_NAME")
    print("Current LOCATION_NAME:", location)
    weather_requester = WeatherRequester(location)
    location_id = weather_requester.get_location_id()
    print("Current LOCATION_ID:", location_id)
    if location_id:
        while True:
            weather_requester.print_data(location_id)
            time.sleep(30)
