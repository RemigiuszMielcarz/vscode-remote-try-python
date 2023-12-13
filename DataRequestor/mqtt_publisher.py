import paho.mqtt.client as mqtt

class MqttPublisher:
    def __init__(self, broker_url, broker_port, username, password):
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.connect(broker_url, broker_port, 60)

    def publish(self, topic, message):
        self.client.publish(topic, message)
