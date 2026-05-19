"""
Agent 工具集 — 供 Qwen-Max tool_use 调用
每个工具函数签名: tool_xxx(video_path, **kwargs) -> (result_dict, summary_str)
"""

import json
import re

import cv2
import numpy as np

import dashscope
from dashscope import MultiModalConversation

from video_utils import extract_frame, crop_region, frame_to_base64


# ── Qwen tool_use 格式的工具定义 ──────────────────────────────────────

TOOL_ANALYZE_SCENE = {
    "type": "function",
    "function": {
        "name": "analyze_scene_frame",
        "description": (
            "用 Qwen-VL 分析指定帧的场景语义：道路类型、禁停标志位置、"
            "停车区域划分。用于理解违停判定的场景背景。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "frame_index": {
                    "type": "integer",
                    "description": "要分析的帧序号（从 0 开始）"
                },
                "focus": {
                    "type": "string",
                    "description": "分析重点，如 'road_markings'、'parking_signs' 或 'general'",
                    "default": "general"
                }
            },
            "required": ["frame_index"]
        }
    }
}

TOOL_RECOGNIZE_PLATE = {
    "type": "function",
    "function": {
        "name": "recognize_license_plate",
        "description": "对指定帧的指定区域进行车牌识别，返回车牌号字符串。",
        "parameters": {
            "type": "object",
            "properties": {
                "frame_index": {
                    "type": "integer",
                    "description": "要识别的帧序号"
                },
                "bbox": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "车辆区域 [x1, y1, x2, y2]（像素坐标）"
                }
            },
            "required": ["frame_index", "bbox"]
        }
    }
}

TOOL_MOTION_ANALYSIS = {
    "type": "function",
    "function": {
        "name": "analyze_motion_in_region",
        "description": (
            "用 OpenCV 帧差法分析视频中某区域在指定帧范围内的运动量，"
            "判断是否存在静止车辆。avg_motion_score < 3.0 视为静止。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "bbox": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "分析区域 [x1, y1, x2, y2]"
                },
                "start_frame": {
                    "type": "integer",
                    "description": "起始帧序号"
                },
                "end_frame": {
                    "type": "integer",
                    "description": "结束帧序号"
                }
            },
            "required": ["bbox", "start_frame", "end_frame"]
        }
    }
}

ALL_TOOLS = [TOOL_ANALYZE_SCENE, TOOL_RECOGNIZE_PLATE, TOOL_MOTION_ANALYSIS]


# ── 工具实现 ──────────────────────────────────────────────────────────

def tool_analyze_scene_frame(video_path: str, frame_index: int, focus: str = "general") -> tuple:
    frame = extract_frame(video_path, frame_index)
    if frame is None:
        return {"error": "帧提取失败"}, "场景分析失败：无法提取帧"

    img_b64 = frame_to_base64(frame)
    focus_hint = {
        "road_markings": "重点识别道路标线（黄线、白线、禁停线）的位置和含义",
        "parking_signs": "重点识别禁停标志、限时停车标志等交通标志",
        "general": "全面分析停车场景",
    }.get(focus, "全面分析停车场景")

    prompt = (
        f"请分析这一帧的停车场景。{focus_hint}。"
        "以 JSON 格式输出，包含字段："
        "road_type（道路类型，如：校园道路/主干道/停车场）、"
        "no_parking_signs（禁停标志列表，每项含 description 和 location）、"
        "parking_zones（停车区域描述）、"
        "scene_summary（一句话总结场景和违停风险）。"
        "只输出 JSON，不要其他内容。"
    )

    try:
        resp = MultiModalConversation.call(
            model="qwen-vl-max",
            messages=[{
                "role": "user",
                "content": [
                    {"image": f"data:image/jpeg;base64,{img_b64}"},
                    {"text": prompt}
                ]
            }]
        )
        text = resp.output.choices[0].message.content[0].get("text", "")
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        result = json.loads(json_match.group()) if json_match else {"raw": text}
    except Exception as e:
        result = {"error": str(e)}

    summary = result.get("scene_summary", result.get("raw", "场景分析完成")[:80])
    return result, f"场景分析：{summary}"


def tool_recognize_license_plate(video_path: str, frame_index: int, bbox: list) -> tuple:
    frame = extract_frame(video_path, frame_index)
    if frame is None:
        return {"plate": "N/A", "error": "帧提取失败"}, "车牌识别失败：无法提取帧"

    cropped = crop_region(frame, bbox)
    img_b64 = frame_to_base64(cropped)

    try:
        resp = MultiModalConversation.call(
            model="qwen-vl-max",
            messages=[{
                "role": "user",
                "content": [
                    {"image": f"data:image/jpeg;base64,{img_b64}"},
                    {"text": "请识别图中车辆的车牌号。只输出车牌号，无法识别则输出 N/A。"}
                ]
            }]
        )
        plate = resp.output.choices[0].message.content[0].get("text", "N/A").strip()
    except Exception as e:
        plate = "N/A"

    return {"plate": plate}, f"车牌识别：{plate}"


def tool_analyze_motion_in_region(video_path: str, bbox: list, start_frame: int, end_frame: int) -> tuple:
    x1, y1, x2, y2 = [int(v) for v in bbox]
    cap = cv2.VideoCapture(video_path)

    prev_gray = None
    motion_scores = []
    sample_step = max(1, (end_frame - start_frame) // 20)

    for fi in range(start_frame, min(end_frame + 1, start_frame + 200 * sample_step), sample_step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ret, frame = cap.read()
        if not ret:
            break
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None and prev_gray.shape == gray.shape:
            diff = cv2.absdiff(prev_gray, gray)
            motion_scores.append(float(np.mean(diff)))
        prev_gray = gray

    cap.release()

    avg_motion = float(np.mean(motion_scores)) if motion_scores else 0.0
    is_stationary = avg_motion < 3.0

    result = {
        "avg_motion_score": round(avg_motion, 3),
        "is_stationary": is_stationary,
        "frames_analyzed": len(motion_scores),
    }
    status = "静止" if is_stationary else "运动中"
    return result, f"运动分析：平均运动量 {avg_motion:.2f}，{status}"


# ── 工具分发表 ────────────────────────────────────────────────────────

TOOL_DISPATCH = {
    "analyze_scene_frame": tool_analyze_scene_frame,
    "recognize_license_plate": tool_recognize_license_plate,
    "analyze_motion_in_region": tool_analyze_motion_in_region,
}
