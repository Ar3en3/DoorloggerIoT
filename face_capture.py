from picamera2 import Picamera2
import cv2
import time
import numpy as np
import os
from datetime import datetime
from bq_logger import log_face_entry


picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

print("Starting Security Cam Mode. Press Ctrl+C to stop.")

try:
    while True:
        print("Capturing image...")
        time.sleep(1)  
        image = picam2.capture_array()

        if image is None:
            print("Failed to capture image.")
            continue

        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        print(f"[INFO] Faces detected: {len(faces)}")

        if len(faces) > 0:
            image_name = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(image_name, image)
            print("[INFO] Face detected. Logging to BigQuery...")
            log_face_entry(image_name)

        time.sleep(5)

except KeyboardInterrupt:
    print("\n[INFO] Security Cam stopped by user.")
