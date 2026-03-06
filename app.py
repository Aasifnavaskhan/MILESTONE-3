import streamlit as st
import cv2
import time
import pythoncom
import pandas as pd
from handgesture import GestureController

st.set_page_config("Hand Gesture Volume Control", layout="wide")
st.title("MILESTONE 3")

# ---------- Session State ----------
if "run" not in st.session_state:
    st.session_state.run = False
if "history" not in st.session_state:
    st.session_state.history = []
if "fps" not in st.session_state:
    st.session_state.fps = 0
if "latency" not in st.session_state:
    st.session_state.latency = 0

# ---------- Controls ----------
c1, c2 = st.columns(2)
if c1.button("▶ Start Camera"):
    st.session_state.run = True
if c2.button("⏹ Stop Camera"):
    st.session_state.run = False

# ---------- Layout ----------
left, right = st.columns([3, 2])

video = left.empty()
status = right.empty()
volume_text = right.empty()
volume_bar = right.progress(0)
graph = right.empty()
perf = right.empty()

# ---------- Camera Loop ----------
if st.session_state.run:
    pythoncom.CoInitialize()
    cap = cv2.VideoCapture(0)
    controller = GestureController()
    prev_time = 0

    while st.session_state.run:
        start_time = time.time()

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame, distance, volume, gesture, hands, muted = controller.process_frame(frame)

        # Latency
        st.session_state.latency = int((time.time() - start_time) * 1000)

        # FPS
        curr_time = time.time()
        st.session_state.fps = int(1 / (curr_time - prev_time + 0.0001))
        prev_time = curr_time

        # History for graph
        st.session_state.history.append(volume)
        if len(st.session_state.history) > 30:
            st.session_state.history.pop(0)

        # Webcam display
        video.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

        # Status panel
        status.markdown(
            f"""
            ✋ **Hands Detected:** {hands}  
            📏 **Distance:** {distance}px  
            🖐 **Gesture:** {gesture}  
            🔊 **Volume:** {"MUTED" if muted else f"{volume}%"}  
            """
        )

        # Volume bar
        volume_text.markdown(f"🔊 **Volume Level:** {volume}%")
        volume_bar.progress(volume / 100)

        # Volume graph
        df = pd.DataFrame({
            "Frame": range(len(st.session_state.history)),
            "Volume": st.session_state.history
        })
        graph.line_chart(df.set_index("Frame"))

        # Performance
        perf.markdown(
            f"""
            ⚡ **FPS:** {st.session_state.fps}  
            ⏱ **Latency:** {st.session_state.latency} ms
            """
        )

        time.sleep(0.03)


    cap.release()
