import json
import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
TOPIC = "frigate/events"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_HOST, 1883, 60)

test_event = {
    "type": "end",
    "after": {
        "id": "1775000214.090971-pi235t",
        "camera": "front_door",
        "label": "person"
    }
}

client.publish(TOPIC, json.dumps(test_event))
print("Test event published!")
client.disconnect()
