# 🚗 Automatic Number Plate Recognition (ANPR) System

A **Flask-based Automatic Number Plate Recognition (ANPR) system** that detects vehicle number plates from uploaded images and stores vehicle information in a MySQL database.

This project uses **YOLOv8 for vehicle detection**, **EasyOCR for text recognition**, and **rule-based validation** for Indian number plate formats.

---

## 📌 Features

* 🔐 **User Authentication:** Secure login and logout functionality.
* 📤 **Image Upload:** Interface to upload vehicle images for processing.
* 🚘 **Vehicle Detection:** Uses YOLOv8 (COCO model) to identify vehicles in the image.
* 🔎 **OCR Recognition:** Extracts text from detected vehicle regions using EasyOCR.
* 🇮🇳 **Indian Format Support:** Specialized validation for Indian number plate patterns.
* 🧠 **Smart Error Correction:** Automatically fixes common OCR confusions (e.g., `O` ↔ `0`, `I` ↔ `1`).
* 📝 **Vehicle Registration:** Store owner details (Name & Phone) associated with plates.
* 🗄️ **MySQL Integration:** robust backend database for data persistence.
* 📋 **Dashboard:** View a list of all registered vehicles.

---

## 🛠️ Tech Stack

* **Language:** Python
* **Web Framework:** Flask
* **Computer Vision:** OpenCV, Ultralytics YOLOv8
* **OCR Engine:** EasyOCR
* **Database:** MySQL
* **Frontend:** HTML, CSS, Bootstrap

---

## 📂 Project Structure

```text
ANPR-Flask/
│
├── main.py                # Flask application entry point
├── anpr.py                # Core ANPR logic (YOLO detection + OCR)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── templates/             # HTML Templates
│   ├── base.html
│   ├── login.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── register.html
│   └── vehicles.html
│
├── static/                # Static assets
│   └── styles.css
│
└── uploads/               # Folder for uploaded images (ignored in Git)
