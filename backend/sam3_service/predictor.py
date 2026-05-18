"""
SAM 3 Video Predictor wrapper for vehicle segmentation and tracking.
Provides both real SAM 3 inference (requires CUDA) and mock mode for development.
"""

import math
import os
import random
import time

import cv2
import numpy as np


VEHICLE_PROMPTS = ["car", "truck", "van", "bus"]
STATIONARY_THRESHOLD_PX = 10  # pixels per second
VIOLATION_DURATION_SEC = 5.0


def _bbox_center(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def analyze_violations(tracks: list, fps: float) -> list:
    """
    Given a list of vehicle tracks, determine which ones are violations.
    A vehicle is in violation if its bbox center moves < STATIONARY_THRESHOLD_PX/sec
    for more than VIOLATION_DURATION_SEC consecutive seconds.
    """
    results = []
    for track in tracks:
        frames = track["frames"]
        if len(frames) < 2:
            results.append({**track, "is_violation": False, "stationary_duration_sec": 0})
            continue

        stationary_start = 0
        max_stationary_duration = 0
        max_stationary_range = (0, 0)

        for i in range(1, len(frames)):
            prev = frames[i - 1]
            curr = frames[i]
            dt = (curr["frame_index"] - prev["frame_index"]) / fps if fps > 0 else 1
            if dt <= 0:
                continue
            cx_prev, cy_prev = _bbox_center(prev["bbox"])
            cx_curr, cy_curr = _bbox_center(curr["bbox"])
            dist = math.sqrt((cx_curr - cx_prev) ** 2 + (cy_curr - cy_prev) ** 2)
            speed = dist / dt

            if speed >= STATIONARY_THRESHOLD_PX:
                duration = (frames[i - 1]["frame_index"] - frames[stationary_start]["frame_index"]) / fps
                if duration > max_stationary_duration:
                    max_stationary_duration = duration
                    max_stationary_range = (frames[stationary_start]["frame_index"], frames[i - 1]["frame_index"])
                stationary_start = i

        # Check final segment
        duration = (frames[-1]["frame_index"] - frames[stationary_start]["frame_index"]) / fps
        if duration > max_stationary_duration:
            max_stationary_duration = duration
            max_stationary_range = (frames[stationary_start]["frame_index"], frames[-1]["frame_index"])

        is_violation = max_stationary_duration >= VIOLATION_DURATION_SEC
        start_sec = round(max_stationary_range[0] / fps, 1) if fps > 0 else 0
        end_sec = round(max_stationary_range[1] / fps, 1) if fps > 0 else 0

        # Pick best frame for license plate recognition (middle of stationary period)
        best_frame_idx = (max_stationary_range[0] + max_stationary_range[1]) // 2
        best_frame_data = next((f for f in frames if f["frame_index"] == best_frame_idx), frames[len(frames) // 2])

        result = {
            "track_id": track["track_id"],
            "class": track["class"],
            "is_violation": is_violation,
            "stationary_duration_sec": round(max_stationary_duration, 1),
            "best_frame_index": best_frame_data["frame_index"],
            "best_frame_bbox": best_frame_data["bbox"],
        }
        if is_violation:
            result["violation_reason"] = (
                f"车辆在第{start_sec}s-{end_sec}s期间静止不动"
                f"（{round(max_stationary_duration, 1)}秒），超过{VIOLATION_DURATION_SEC}秒阈值"
            )
            # Collect bbox samples for the report
            sample_indices = [max_stationary_range[0], best_frame_data["frame_index"], max_stationary_range[1]]
            result["bbox_samples"] = [
                f["bbox"] for f in frames if f["frame_index"] in sample_indices
            ]
        results.append(result)
    return results


class SAM3Predictor:
    """
    Wraps SAM 3 video predictor for vehicle segmentation and tracking.
    Falls back to mock mode when SAM 3 is not available (no CUDA / not installed).
    """

    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.model = None
        if not use_mock:
            try:
                from sam3.model_builder import build_sam3_video_predictor
                self.model = build_sam3_video_predictor()
            except Exception:
                self.use_mock = True

    def process_video(self, video_path: str, progress_callback=None) -> dict:
        """
        Process a video file and return vehicle tracking + violation analysis.
        progress_callback(current_frame, total_frames) is called periodically.
        """
        video_info = _get_video_info(video_path)
        if not video_info:
            return {"error": "无法读取视频文件"}

        if self.use_mock:
            tracks = self._mock_inference(video_info, progress_callback)
        else:
            tracks = self._real_inference(video_path, video_info, progress_callback)

        vehicles = analyze_violations(tracks, video_info["fps"])

        return {
            "fps": video_info["fps"],
            "total_frames": video_info["total_frames"],
            "duration_sec": video_info["duration_sec"],
            "width": video_info["width"],
            "height": video_info["height"],
            "vehicles": vehicles,
        }

    def _real_inference(self, video_path: str, video_info: dict, progress_callback=None) -> list:
        """Run actual SAM 3 inference."""
        response = self.model.handle_request(
            request=dict(type="start_session", resource_path=video_path)
        )
        session_id = response["session_id"]

        all_tracks = []
        for prompt_text in VEHICLE_PROMPTS:
            resp = self.model.handle_request(
                request=dict(
                    type="add_prompt",
                    session_id=session_id,
                    frame_index=0,
                    text=prompt_text,
                )
            )
            outputs = resp.get("outputs", {})
            for obj_id, obj_data in outputs.items():
                track = {
                    "track_id": len(all_tracks) + 1,
                    "class": prompt_text,
                    "frames": [],
                }
                for frame_idx, frame_data in obj_data.items():
                    if frame_data.get("boxes") is not None and len(frame_data["boxes"]) > 0:
                        bbox = frame_data["boxes"][0].tolist()
                        score = float(frame_data.get("scores", [0.9])[0])
                        track["frames"].append({
                            "frame_index": int(frame_idx),
                            "bbox": bbox,
                            "score": score,
                        })
                if track["frames"]:
                    track["frames"].sort(key=lambda f: f["frame_index"])
                    all_tracks.append(track)

            if progress_callback:
                progress_callback(video_info["total_frames"], video_info["total_frames"])

        return all_tracks

    def _mock_inference(self, video_info: dict, progress_callback=None) -> list:
        """Generate realistic mock tracking data for development."""
        fps = video_info["fps"]
        total_frames = video_info["total_frames"]
        w, h = video_info["width"], video_info["height"]

        num_vehicles = random.randint(2, 4)
        tracks = []

        for i in range(num_vehicles):
            track_id = i + 1
            is_stationary = i == 0  # First vehicle is always a violator for testing

            base_x = random.randint(int(w * 0.2), int(w * 0.7))
            base_y = random.randint(int(h * 0.3), int(h * 0.7))
            vw = random.randint(80, 160)
            vh = random.randint(60, 120)

            frames = []
            sample_interval = max(1, int(fps))  # Sample once per second

            for frame_idx in range(0, total_frames, sample_interval):
                if is_stationary:
                    jitter_x = random.uniform(-2, 2)
                    jitter_y = random.uniform(-2, 2)
                else:
                    elapsed = frame_idx / fps
                    jitter_x = elapsed * random.uniform(15, 30)
                    jitter_y = random.uniform(-3, 3)

                bbox = [
                    base_x + jitter_x,
                    base_y + jitter_y,
                    base_x + vw + jitter_x,
                    base_y + vh + jitter_y,
                ]
                frames.append({
                    "frame_index": frame_idx,
                    "bbox": [round(v, 1) for v in bbox],
                    "score": round(random.uniform(0.85, 0.98), 3),
                })

                if progress_callback and frame_idx % (sample_interval * 5) == 0:
                    progress_callback(frame_idx, total_frames)

            tracks.append({
                "track_id": track_id,
                "class": random.choice(VEHICLE_PROMPTS),
                "frames": frames,
            })

        if progress_callback:
            progress_callback(total_frames, total_frames)

        return tracks


def _get_video_info(video_path: str) -> dict | None:
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
        "duration_sec": round(duration, 2),
    }
