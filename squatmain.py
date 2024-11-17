import cv2
import av
import os
import sys
from aiortc.contrib.media import MediaRecorder

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds_beginner, get_thresholds_pro

thresholds = get_thresholds_beginner()
# Initialize processing and pose detection
live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)
pose = get_mediapipe_pose()

# Setup video capture and writer
cap = cv2.VideoCapture(1)  # Use the first webcam
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    sys.exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_video_file = "output_live.avi"
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter(output_video_file, fourcc, fps, (frame_width, frame_height))

print("Press 'q' to stop the video stream.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Process frame
        frame, _ = live_process_frame.process(frame, pose)

        # Display frame
        cv2.imshow("AI Fitness Trainer: Squats Analysis", frame)

        # Save processed frame to video file
        out.write(frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()

