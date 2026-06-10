import os
import cv2
import pickle
import face_recognition

KNOWN_ENCODINGS = []
KNOWN_NAMES = []

DATASET_DIR = "dataset"

for person_name in os.listdir(DATASET_DIR):

    person_folder = os.path.join(
        DATASET_DIR,
        person_name
    )

    if not os.path.isdir(person_folder):
        continue

    print(
        f"Processing {person_name}"
    )

    for image_name in os.listdir(
        person_folder
    ):

        image_path = os.path.join(
            person_folder,
            image_name
        )

        image = cv2.imread(
            image_path
        )

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        faces = face_recognition.face_locations(
            rgb
        )

        encodings = face_recognition.face_encodings(
            rgb,
            faces
        )

        for encoding in encodings:

            KNOWN_ENCODINGS.append(
                encoding
            )

            KNOWN_NAMES.append(
                person_name
            )

print(
    f"Total Faces: {len(KNOWN_NAMES)}"
)

data = {

    "encodings":
    KNOWN_ENCODINGS,

    "names":
    KNOWN_NAMES

}

with open(
    "encodings.pkl",
    "wb"
) as f:

    pickle.dump(
        data,
        f
    )

print(
    "Encoding Saved"
)