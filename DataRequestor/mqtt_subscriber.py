import os
import errno
import paho.mqtt.client as mqtt

class MqttSubscriber:
    def __init__(self, broker_url, broker_port, username, password):
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.on_message = self.on_message
        self.client.connect(broker_url, broker_port, 60)


    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        parts = topic.split('/')
        if len(parts) >= 2:
            student_index = parts[0]
            location = parts[1]
            filename = f"{student_index}-{location}.txt"
            directory = os.path.join(os.getcwd(), student_index)

            try:
                os.makedirs(directory, exist_ok=True)
            except TypeError:
                try:
                    os.makedirs(directory)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(directory):
                        pass
                    else:
                        raise

            file_path = os.path.join(directory, filename)
            with open(file_path, "w") as file:
                file.write(payload)
            print(f"Saved message to {file_path}")
        else:
            print(f"Invalid topic format: {topic}")


    def subscribe(self, topic):
        self.client.subscribe(topic)
        self.client.loop_forever()
