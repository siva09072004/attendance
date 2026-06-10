from flask import Flask, render_template, request, jsonify
import os
import base64
import qrcode
import datetime
import face_recognition
import qrcode
from config import MONGO_URI


from pymongo import MongoClient

app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="static"
)

# MongoDB


client = MongoClient(MONGO_URI)

db = client["attendance_system"]

# routes here ...

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

import os

import sys

@app.route("/start-attendance")
def start_attendance():

    try:

        print("START BUTTON CLICKED")

        subprocess.Popen(
            [sys.executable, "attendance_fr.py"]
        )

        print("ATTENDANCE FILE STARTED")

        return jsonify({
            "status":"success"
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "status":"error",
            "message":str(e)
        })

@app.route(
    "/generate_qr",
    methods=["POST"]
)
def generate_qr():

    student_name = request.json["name"]

    base_url = request.host_url

    qr_data = (
        f"{base_url}mobile-register"
        f"?name={student_name}"
    )

    os.makedirs(
        "static/qr",
        exist_ok=True
    )

    qr_path = (
        f"static/qr/{student_name}.png"
    )

    qr = qrcode.make(
        qr_data
    )

    qr.save(
        qr_path
    )

    print(qr_data)

    return jsonify({
        "qr":
        f"/static/qr/{student_name}.png"
    })

@app.route(
"/upload_image",
methods=["POST"]
)
def upload_image():
    try:
        data = request.json

        student_name = data["name"].strip().upper()

        image_data = data["image"]

        image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(
            image_data
        )

        # -------------------------
        # Create Student Folder
        # -------------------------

        folder = os.path.join(
            "dataset",
            student_name
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        image_count = len(
            os.listdir(folder)
        ) + 1

        image_path = os.path.join(
            folder,
            f"{image_count}.jpg"
        )

        with open(
            image_path,
            "wb"
        ) as f:

            f.write(
                image_bytes
            )

        # -------------------------
        # FACE VALIDATION
        # -------------------------

        image = face_recognition.load_image_file(
            image_path
        )

        faces = face_recognition.face_locations(
            image
        )

        if len(faces) == 0:

            os.remove(
                image_path
            )

            return jsonify({
                "status":"error",
                "message":"No Face Detected"
            })

        if len(faces) > 1:

            os.remove(
                image_path
            )

            return jsonify({
                "status":"error",
                "message":"Multiple Faces Detected"
            })

        # -------------------------
        # MongoDB Update
        # -------------------------
        
        students = db["students"]

        uploaded_time = str(
            datetime.datetime.now()
        )

        existing_student = students.find_one(
            {
                "name":student_name
            }
        )

        if existing_student:

            students.update_one(

                {
                    "name":student_name
                },

                {
                    "$push":{
                        "images":{
                            "path":image_path,
                            "uploaded_at":
                            uploaded_time
                        }
                    },

                    "$inc":{
                        "image_count":1
                    }
                }
            )

        else:

            students.insert_one({

                "name":student_name,

                "images":[
                    {
                        "path":image_path,
                        "uploaded_at":
                        uploaded_time
                    }
                ],

                "image_count":1,

                "registration_completed":False,

                "encoding_created":False,

                "registered_date":
                str(
                    datetime.date.today()
                )
            })

        student = students.find_one(
            {
                "name":student_name
            }
        )

        if student["image_count"] >= 20:

            students.update_one(

                {
                    "name":student_name
                },

                {
                    "$set":{
                        "registration_completed":True
                    }
                }
            )

        return jsonify({

            "status":"success",

            "message":"Image Saved"

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )