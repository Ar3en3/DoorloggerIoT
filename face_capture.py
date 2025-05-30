import os
import cv2
import numpy as np
import face_recognition
from picamera2 import Picamera2, Preview
from libcamera import Transform
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import storage
import requests
from bq_logger import log_face_entry

load_dotenv()

GCS_BUCKET_NAME = os.getenv("BUCKET_NAME")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

storage_client = storage.Client.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
bucket = storage_client.bucket(GCS_BUCKET_NAME)

print("[INFO] Loading known faces...")
known_face_encodings = []
known_face_names = []

KNOWN_FACES_DIR = "known_faces"
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

print(f"[INFO] Loaded {len(known_face_encodings)} known faces.")

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}, transform=Transform(hflip=1, vflip=1))
picam2.configure(config)
picam2.start()

print("Security cam running. Ctrl+C to exit.")

try:
    while True:
        frame = picam2.capture_array()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        rgb_frame = cv2.flip(rgb_frame, 0)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        print(f"[DEBUG] Detected {len(face_locations)} face(s)")

        for location, encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, encoding)
            name = "Unknown"

            if True in matches:
                best_match_index = matches.index(True)
                name = known_face_names[best_match_index]
                print(f"[INFO] Welcome back, {name}")
            else:
                print("[ALERT] Unknown person detected!")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.jpg"
            filepath = os.path.join("captures", filename)
            os.makedirs("captures", exist_ok=True)
            cv2.imwrite(filepath, rgb_frame)

            blob = bucket.blob(f"captures/{filename}")
            blob.upload_from_filename(filepath)
            print(f"[CLOUD] Uploaded {filename} to GCS.")

            log_face_entry(filename, name)

            if name == "Unknown":
                with open(filepath, "rb") as f:
                    response = requests.post(
                        DISCORD_WEBHOOK_URL,
                        files={"file": (filename, f)},
                        data={"content": f"Unknown face detected at {timestamp}"}
                    )
                    print(f"[DISCORD] Notification sent, status: {response.status_code}")


except KeyboardInterrupt:
    print("Exiting security cam.")
    picam2.stop()
    cv2.destroyAllWindows()
