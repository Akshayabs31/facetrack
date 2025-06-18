import cv2
import dlib
import os
from imutils import face_utils
from scipy.spatial import distance

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3

# Dynamically get the correct file path for the predictor
current_dir = os.path.dirname(os.path.abspath(__file__))
predictor_path = os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def run_anti_spoof():
    blink_count = 0
    consec = 0
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            if ear < EYE_AR_THRESH:
                consec += 1
            else:
                if consec >= EYE_AR_CONSEC_FRAMES:
                    blink_count += 1
                consec = 0

            cv2.putText(frame, f"Blinks: {blink_count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Anti-Spoof Check", frame)
        key = cv2.waitKey(1) & 0xFF
        if blink_count >= 1:
            cap.release()
            cv2.destroyAllWindows()
            return "real"
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return "spoof"