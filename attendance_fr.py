import cv2
import face_recognition
import pickle
import csv
import os
from datetime import datetime

# -----------------------
# Load Encodings
# -----------------------
with open("encodings.pkl", "rb") as f:
    known_encodings, known_names = pickle.load(f)

# -----------------------
# Attendance Function
# -----------------------
def mark_attendance(name):

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    if not os.path.exists("attendance.csv"):

        with open(
            "attendance.csv",
            "w",
            newline=""
        ) as f:

            writer = csv.writer(f)

            writer.writerow(
                ["Name", "Date", "Time"]
            )

    with open(
        "attendance.csv",
        "r"
    ) as f:

        reader = csv.reader(f)

        for row in reader:

            if len(row) < 3:
                continue

            if (
                row[0] == name
                and
                row[1] == today
            ):
                return False

    with open(
        "attendance.csv",
        "a",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [name, today, current_time]
        )

    return True


# -----------------------
# Webcam
# -----------------------
cap = cv2.VideoCapture(0)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)

message = ""

while True:

    success, frame = cap.read()

    if not success:
        break

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    face_locations = face_recognition.face_locations(
        rgb
    )

    face_encodings = face_recognition.face_encodings(
        rgb,
        face_locations
    )

    for face_encoding, face_location in zip(
        face_encodings,
        face_locations
    ):

        matches = face_recognition.compare_faces(
            known_encodings,
            face_encoding,
            tolerance=0.5
        )

        face_distances = face_recognition.face_distance(
            known_encodings,
            face_encoding
        )

        best_match_index = face_distances.argmin()

        if (
            matches[best_match_index]
        ):

            name = known_names[
                best_match_index
            ]

            distance = face_distances[
                best_match_index
            ]

            match_percent = int(
                (1 - distance) * 100
            )

            attendance_status = (
                mark_attendance(name)
            )

            if attendance_status:

                message = (
                    f"{name} Attendance Marked"
                )

            else:

                message = (
                    f"{name} Already Present"
                )

        else:

            name = "UNKNOWN"

            match_percent = 0

            message = (
                "Unknown Person"
            )

        top, right, bottom, left = (
            face_location
        )

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            f"{name} | {match_percent}%",
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.rectangle(
        frame,
        (0, frame.shape[0] - 50),
        (frame.shape[1], frame.shape[0]),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        message,
        (20, frame.shape[0] - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.imshow(
        "Face Recognition Attendance",
        frame
    )

    if (
        cv2.waitKey(1)
        & 0xFF
        == ord("q")
    ):
        break

cap.release()
cv2.destroyAllWindows()