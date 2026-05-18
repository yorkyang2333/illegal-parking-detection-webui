import cv2
import numpy as np
import base64
import os


def extract_frame(video_path: str, frame_index: int) -> np.ndarray | None:
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None


def crop_region(frame: np.ndarray, bbox: list) -> np.ndarray:
    x1, y1, x2, y2 = [int(v) for v in bbox]
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    return frame[y1:y2, x1:x2]


def frame_to_base64(frame: np.ndarray, fmt: str = ".jpg") -> str:
    _, buffer = cv2.imencode(fmt, frame)
    return base64.b64encode(buffer).decode("utf-8")


def get_video_info(video_path: str) -> dict | None:
    if not os.path.exists(video_path):
        return None
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    duration = total_frames / fps if fps > 0 else 0
    return {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_sec": round(duration, 2)
    }
