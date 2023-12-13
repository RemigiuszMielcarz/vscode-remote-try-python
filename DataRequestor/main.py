import os
import requests
import time
import threading
from datetime import datetime
from mqtt_publisher import MqttPublisher
from mqtt_subscriber import MqttSubscriber


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


# Define the function to handle subscription in a separate thread
def start_mqtt_subscriber(broker_url, broker_port, username, password, topic):
    mqtt_subscriber = MqttSubscriber(broker_url, broker_port, username, password)
    mqtt_subscriber.subscribe(topic)
    mqtt_subscriber.client.loop_forever()


if __name__ == "__main__":
    broker_url = os.getenv("BROKER_URL")
    broker_port = int(os.getenv("BROKER_PORT"))
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    location = os.getenv("LOCATION_NAME")

    # LOCALIZATION
    print("Current LOCATION_NAME:", location)
    weather_requester = WeatherRequester(location)

    # LOCALIZATION ID
    location_id = weather_requester.get_location_id()
    print("Current LOCATION_ID:", location_id)

    # Initialize the MQTT publisher
    mqtt_publisher = MqttPublisher(broker_url, broker_port, username, password)

    # Start the MQTT subscriber in a separate thread
    subscriber_topic = f"{location_id}/{location}"
    subscriber_thread = threading.Thread(target=start_mqtt_subscriber, args=(broker_url, broker_port, username, password, subscriber_topic))
    subscriber_thread.daemon = True  # This will allow the main program to exit even if the thread is running
    subscriber_thread.start()

    if location_id:
            while True:
                weather_data = weather_requester.fetch_data(location_id)
                if weather_data:
                    formatted_data = weather_requester.format_data(weather_data)
                    print(formatted_data)
                    topic = f"{location_id}/{location}"
                    mqtt_publisher.publish(topic, str(formatted_data))
                time.sleep(30)