import cv2
import numpy as np
from typing import List
import os


def extract_frames(video_path: str) -> List[np.array]:
    """
    """
    all_frames: List[np.array] = []

    video_capture = cv2.VideoCapture(video_path)

    success, frame = video_capture.read()

    while success:
        print('loading')
        cv2.imwrite('/tmp/frame.png', frame)

        os.system(
            'convert /tmp/frame.png -fuzz 8% -transparent white /tmp/frame.png'
        )

        frame = cv2.imread('/tmp/frame.png', cv2.IMREAD_UNCHANGED)
        frame = cv2.flip(frame, 0)

        all_frames.append(frame)

        success, frame = video_capture.read()

    video_capture.release()

    return all_frames
