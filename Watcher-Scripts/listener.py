import os
import json
import requests
import paho.mqtt.client as mqtt

# Grab settings from Docker environment variables
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
FRIGATE_HOST = os.getenv("FRIGATE_HOST", "localhost")
TOPIC = "frigate/events"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        event_type = data.get("type") # 'new', 'update', or 'end'
        
        # We act when the event ends so the video clip is fully written
        if event_type == "end":
            event_id = data["after"]["id"]
            camera = data["after"]["camera"]
            label = data["after"]["label"]
            
            print(f"Event ended: {label} on {camera}. Downloading clip...")
            
            # Request the clip from Frigate API
            clip_url = f"http://{FRIGATE_HOST}:5000/api/events/{event_id}/clip.mp4"
            response = requests.get(clip_url)
            
            if response.status_code == 200:
                filename = f"{camera}_{event_id}.mp4"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully saved {filename}")
                # ADD YOUR CUSTOM BASH/UPLOAD COMMAND HERE
            else:
                print(f"Failed to fetch clip. Status: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to {MQTT_HOST}...")
client.connect(MQTT_HOST, 1883, 60)
client.loop_forever()
