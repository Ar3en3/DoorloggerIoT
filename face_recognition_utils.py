import face_recognition
import os

def load_known_faces(known_faces_dir):
    known_encodings = []
    known_names = []

    for person_name in os.listdir(known_faces_dir):
        person_folder = os.path.join(known_faces_dir, person_name)

        if not os.path.isdir(person_folder):
            continue

        for filename in os.listdir(person_folder):
            image_path = os.path.join(person_folder, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person_name)

    return known_encodings, known_names
