# FACETRACK – Face Recognition Attendance System with Anti-Spoofing & Admin Panel

FACETRACK is a smart, real-time face recognition-based attendance system built using Python, Streamlit, OpenCV, and dlib. It includes an admin dashboard, face registration, live tracking, anti-spoofing measures, and detailed attendance logging.

---
login
#username: admin
#password: abc12345

## 🚀 Features

- 🎥 Real-time face detection and recognition using webcam
- 🧠 Face encoding and matching with pre-trained models
- 🙅‍♀️ Anti-spoofing using 68-point facial landmarks
- 🧾 Auto-generated CSV attendance with timestamps
- 🧑‍💼 Admin login & dashboard to monitor records
- 📄 Streamlit-based UI for a seamless user experience
- 📸 Image dataset stored locally and converted to embeddings

---

## 🗂️ Project Structure

```
FACETRACK/
├── Tracking.py                  # Main recognition/tracking script
├── config.yaml                 # Config for dataset/model paths
├── admin_config.yaml           # Admin credentials or config
├── requirements.txt            # Python dependencies
├── dataset/                    # Images of known persons + encoded .pkl file
│   ├── 1_Elon_Musk.jpg
│   ├── ...
│   └── database.pkl
├── register/attendance.csv     # Auto-updated attendance logs
├── assets/                     # UI elements (images, gif)
├── pages/                      # Streamlit multi-page interface
│   ├── 0_🔒_Admin.py
│   └── ...
├── admin/                      # Admin authentication/dashboard scripts
│   ├── admin_auth.py
│   └── admin_dashboard.py
├── anti_spoof/                 # Anti-spoofing logic
│   ├── anti_spoof.py
│   └── shape_predictor_68_face_landmarks.dat
├── templates/                  # HTML template for report generation
└── utils.py                    # Shared utility functions
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/FACETRACK.git
cd FACETRACK
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> If dlib installation fails, make sure to install CMake and required build tools:
> - Windows: `pip install cmake`
> - Linux: `sudo apt install build-essential cmake`

---

## ▶️ Running the App

```bash
streamlit run Tracking.py
```

Once launched, use the sidebar to navigate through:
- **Admin Login**
- **Face Registration**
- **Live Face Tracking**
- **View Attendance Data**

---

## 👤 How to Add New Faces

1. Add a clear frontal image of the person in the `dataset/` folder using the format:
   ```
   [ID]_[Full_Name].jpg
   e.g., 4_Tony_Stark.jpg
   ```
2. Use the **Register** page from the UI to encode and store the new face.

---

## 📋 Attendance Logs

- Logged into `register/attendance.csv`
- Includes:
  - Name
  - Time
  - Date

---

## 🔐 Admin Panel

- Navigate to **Admin Login** from the sidebar
- Credentials can be configured in `admin_config.yaml`
- Features include:
  - Viewing registered users
  - Monitoring attendance logs
  - Admin-exclusive controls

---

## 🧠 Anti-Spoofing

To avoid false detection (like showing a photo), the system uses:
- **`dlib`'s 68 facial landmarks model** to verify real human movement/structure
- Facial geometry validation before logging attendance

---

## 📄 Dependencies

Key Python packages:
- `face_recognition`
- `opencv-python`
- `dlib`
- `streamlit`
- `numpy`
- `pyyaml`
- `pandas`

Install them all with:
```bash
pip install -r requirements.txt
```

---

## 🙏 Credits

- 📍 Anti-spoofing uses dlib’s [68-point shape predictor](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2), trained by **Davis King**
- 🎓 App structure and attendance system were inspired by [DATCT's Face Recognition Attendance System](https://github.com/datct/Face-Recognition-Attendance-System)
- 🙌 Thanks to the open-source community for their contributions and models

---

## 📜 License

This project is licensed under the **MIT License**. You're free to use, modify, and distribute — just make sure to give proper credit to the original authors and referenced repositories.

---
