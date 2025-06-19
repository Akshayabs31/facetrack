import streamlit as st
import cv2
import face_recognition as frg
import yaml
import dlib
from imutils import face_utils
from scipy.spatial import distance
from utils import recognize, build_dataset
import csv
from datetime import datetime
import os
import pandas as pd
import base64
from pathlib import Path
import time

REGISTER_DIR = 'register'
REGISTER_FILE = f'{REGISTER_DIR}/attendance.csv'
PREDICTOR_PATH = "anti_spoof/shape_predictor_68_face_landmarks.dat"

Path(REGISTER_DIR).mkdir(exist_ok=True)

def register_attendance(name, user_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {'name': name, 'id': user_id, 'timestamp': timestamp}
    file_exists = os.path.isfile(REGISTER_FILE)
    with open(REGISTER_FILE, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)

def is_blinking(ear, blink_thresh=0.21):
    return ear < blink_thresh

def calculate_ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def main():
    st.set_page_config(layout="wide")
    st.title("Face Recognition with Anti-Spoofing (Blink Detection)")

    if st.button("Start Face Recognition"):
        try:
            cfg = yaml.safe_load(open('config.yaml', 'r'))
            WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']
        except:
            st.error("Error in config.yaml")
            return

        FRAME_WINDOW = st.image([])
        st.sidebar.info(WEBCAM_PROMPT)
        name_container = st.sidebar.empty()
        id_container = st.sidebar.empty()

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            st.error("Could not access webcam")
            return

        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(PREDICTOR_PATH)
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        tolerance = st.sidebar.slider("Recognition Tolerance", 0.3, 0.6, 0.45, 0.01)

        st.warning("Please blink 2 times to verify you're real...")

        blink_count = 0
        consec_blink_frames = 0
        EAR_THRESHOLD = 0.21
        EYE_AR_CONSEC_FRAMES = 3
        required_blinks = 2
        start_time = time.time()
        blink_timeout = 10

        recognized = False

        while True:
            ret, frame = cam.read()
            if not ret:
                st.warning("Failed to read from webcam")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rects = detector(gray, 0)

            cv2.putText(frame, f"Blinks: {blink_count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            for rect in rects:
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = calculate_ear(leftEye)
                rightEAR = calculate_ear(rightEye)
                ear = (leftEAR + rightEAR) / 2.0

                if is_blinking(ear, EAR_THRESHOLD):
                    consec_blink_frames += 1
                else:
                    if consec_blink_frames >= EYE_AR_CONSEC_FRAMES:
                        blink_count += 1
                    consec_blink_frames = 0

                if blink_count >= required_blinks:
                    locations = frg.face_locations(rgb)
                    if locations:
                        (top, right, bottom, left) = locations[0]
                        image, name, user_id = recognize(frame, tolerance)

                        if name != "Unknown":
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(frame, f"{name}", (left, top - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            register_attendance(name, user_id)
                            name_container.info(f"Name: {name}")
                            id_container.success(f"ID: {user_id}")
                            st.success(f"✅ {name} verified successfully!")
                            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            recognized = True
                            cam.release()
                            break
                        else:
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            cv2.putText(frame, "Unknown", (left, top - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if blink_count < required_blinks and (time.time() - start_time) > blink_timeout:
                st.error("❌ Face not verified. Not enough blinks.")
                cam.release()
                break

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if os.path.exists(REGISTER_FILE):
            st.sidebar.subheader("Recent Attendance")
            df = pd.read_csv(REGISTER_FILE)
            st.sidebar.dataframe(df.tail(5))
            if st.sidebar.button("Download Report"):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                st.markdown(f'<a href="data:file/csv;base64,{b64}" download="attendance.csv">Download CSV</a>',
                            unsafe_allow_html=True)

        with st.sidebar.expander("Developer Tools"):
            if st.button("Rebuild Dataset"):
                build_dataset()
                st.success("Dataset rebuilt")

if __name__ == "__main__":
    main()