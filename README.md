# Milestone 3 – Volume Mapping and Control Module

## Project Overview
This project demonstrates a hand gesture–controlled system volume application using computer vision techniques.

The system captures live webcam input, detects hand landmarks using MediaPipe, calculates the distance between thumb and index finger, and maps this distance to system volume levels ranging from 0% to 100%.

## Milestones Covered
- **Milestone 1:** Webcam input and real-time hand detection
- **Milestone 2:** Gesture recognition and distance measurement
- **Milestone 3:** Volume mapping, real-time volume control, and graphical visualization

## Technologies Used
- Python
- OpenCV
- MediaPipe
- Streamlit
- Pycaw (Windows system volume control)

## Features
- Real-time hand landmark detection
- Gesture-based volume control
- Smooth volume transitions
- Live volume level display
- Real-time volume graph visualization

## How to Run
```bash
pip install -r requirements.txt
python run_app.py
```
---
