import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class GestureController:
    def __init__(self, det_conf=0.7, trk_conf=0.7, max_hands=1):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            min_detection_confidence=det_conf,
            min_tracking_confidence=trk_conf,
            max_num_hands=max_hands
        )

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        self.volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
        self.min_vol, self.max_vol = self.volume_ctrl.GetVolumeRange()[:2]

        self.is_muted = False

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        distance = 0
        volume_percent = 0
        gesture = "None"
        hands_detected = 0

        if results.multi_hand_landmarks:
            hands_detected = len(results.multi_hand_landmarks)
            hand = results.multi_hand_landmarks[0]

            self.mp_draw.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS
            )

            thumb = hand.landmark[4]
            index = hand.landmark[8]

            x1, y1 = int(thumb.x * w), int(thumb.y * h)
            x2, y2 = int(index.x * w), int(index.y * h)

            distance = int(math.hypot(x2 - x1, y2 - y1))

            # -------- Gesture + Volume Logic --------
            if distance < 40:
                gesture = "Closed"
                self.volume_ctrl.SetMute(1, None)
                self.is_muted = True
                volume_percent = 0
            else:
                self.volume_ctrl.SetMute(0, None)
                self.is_muted = False

                clipped = np.clip(distance, 40, 180)
                vol = np.interp(clipped, [40, 180],
                                [self.min_vol, self.max_vol])
                self.volume_ctrl.SetMasterVolumeLevel(vol, None)

                volume_percent = int(
                    np.interp(clipped, [40, 180], [0, 100])
                )

                if distance < 100:
                    gesture = "Pinch"
                else:
                    gesture = "Open"

            # -------- Visuals --------
            color = (0, 0, 255) if self.is_muted else (0, 255, 0)

            cv2.circle(frame, (x1, y1), 10, color, cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, color, cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), color, 3)

            # -------- Overlay Text (Milestone-2 style) --------
            cv2.putText(frame, f"Gesture: {gesture}",
                        (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (255, 255, 0), 2)

            cv2.putText(frame, f"Distance: {distance}px",
                        (30, 80), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 255, 255), 2)

            cv2.putText(frame, f"Volume: {volume_percent}%",
                        (30, 120), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 255, 0), 2)

            if self.is_muted:
                cv2.putText(frame, "MUTED",
                            (30, 160),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.1, (0, 0, 255), 3)

        return frame, distance, volume_percent, gesture, hands_detected, self.is_muted