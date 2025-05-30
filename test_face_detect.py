from picamera2 import Picamera2
import face_recognition
import numpy as np
import time
import cv2

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)

frame = picam2.capture_array()
face_locations = face_recognition.face_locations(frame)
print(f"[TEST] Faces detected: {len(face_locations)}")

picam2.stop()
