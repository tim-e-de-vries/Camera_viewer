from asyncio import sleep
from cProfile import label
import os
import json
import threading
import requests
import paho.mqtt.client as mqtt
import google.cloud.storage as storage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import time
import os
from dotenv import load_dotenv
import threading

# This only loads the .env file if it exists locally. 
# In Docker, the variables are already in the environment, so this is skipped.
load_dotenv()
# Grab settings from Docker environment variables
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
FRIGATE_HOST = os.getenv("FRIGATE_HOST", "localhost")
GCS_PROJECT = os.getenv("GCS_PROJECT")
GCS_BUCKET = os.getenv("GCS_BUCKET")
sender_email = os.getenv("sender_email")
password = os.getenv("password")
recipient_email = os.getenv("recipient_email")

subject = "New Frigate Event Clip"

TOPIC = "frigate/events"
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_embedded_url_email(sender_email, password, recipient_email, subject, target_url):
    # 1. Setup the MIME message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject + " at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message["From"] = sender_email
    message["To"] = recipient_email

    # 2. Create the HTML body with an embedded link
    # We use an <a> tag to mask the URL with display text
    html_content = f"""
    <html>
      <body>
        <p>Hello,<br><br>
           Please click the button below to visit our site:<br><br><br>
           <a href="{target_url}" style="padding: 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">
           Visit Website
           </a>
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part = MIMEText(html_content, "html")

    # Add HTML part to MIMEMultipart message
    message.attach(part)

    # 3. Connect to the server and send
    # Example using Gmail's SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()

def send_to_cloud_storage(file_path):

    # Placeholder function to upload file to cloud storage
    # Implement your cloud storage upload logic here (e.g., AWS S3, Google Cloud Storage)
    print(f"Uploading {file_path} to cloud storage...")
    # Example: upload_to_s3(file_path)
    client = storage.Client(project=GCS_PROJECT)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)
    print(f"Uploaded to gs://{GCS_BUCKET}/{file_path}")

def process_event(camera, event_id, label):

    time.sleep(30.0)  # Wait for the clip to be fully written

    # Request the clip from Frigate API
    clip_url = f"http://{FRIGATE_HOST}:5000/api/events/{event_id}/clip.mp4"
    response = requests.get(clip_url)

    if response.status_code == 200:
        filename = f"{camera}_{event_id}.mp4"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Successfully saved {filename}")
        send_to_cloud_storage(filename)
        send_embedded_url_email(sender_email, password, recipient_email, subject, f"https://storage.googleapis.com/{GCS_BUCKET}/{filename}")
    else:
        print(f"Failed to fetch clip. Status: {response.status_code}")

def on_connect(client, userdata, connect_flags, rc, properties):
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

            thread = threading.Thread(
                target=process_event, 
                args=(camera, event_id, label)
            )
            thread.start()
            print(f"Started background task for event {event_id}")
            #process_event(camera, event_id, label)
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to {MQTT_HOST}...")
client.connect(MQTT_HOST, 1883, 60)
client.loop_forever()
