
import os
import cv2
import math
import json
import numpy as np
import base64
import dashscope
from http import HTTPStatus
import shutil
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from dotenv import dotenv_values

app = Flask(__name__)

# [TODO] 设置好自己的apikey and frame_cached_root path
config = dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))
api_key = config.get("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("Please set the DASHSCOPE_API_KEY environment variable in the .env file.")

dashscope.api_key = api_key
model_max_tokens = 30720  # DashScope模型的最大Token数
frame_max_tokens = 16384  # DashScope模型每帧的最大Token数
frame_cached_root = os.path.join(os.path.dirname(__file__), "dashscope_cache")

if not os.path.exists(frame_cached_root):
    os.makedirs(frame_cached_root)

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

def token_calculate(image_height, image_width):
    h_bar = round(image_height / 28) * 28
    w_bar = round(image_width / 28) * 28
    min_pixels = 28 * 28 * 4
    max_pixels = 1280 * 28 * 28
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((image_height * image_width) / max_pixels)
        h_bar = math.floor(image_height / beta / 28) * 28
        w_bar = math.floor(image_width / beta / 28) * 28
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (image_height * image_width))
        h_bar = math.ceil(image_height * beta / 28) * 28
        w_bar = math.ceil(image_width * beta / 28) * 28
    total_tokens = int((h_bar * w_bar) / (28 * 28)) + 2
    return total_tokens

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    clear_cache()
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    video_path = os.path.join(frame_cached_root, video_file.filename)
    video_file.save(video_path)

    auto_mode = request.form.get('auto_mode', 'true').lower() == 'true'
    fix_fps = int(request.form.get('fps', 5))
    fix_frames = int(request.form.get('frames', 15))

    frames_path, prompt = extract_video_frames(video_path, auto_mode, fix_fps, fix_frames)

    if not frames_path:
        return jsonify({'error': 'Failed to process video'}), 500

    return jsonify({
        'frames_path': [os.path.basename(p) for p in frames_path],
        'prompt': prompt
    })

@app.route('/frames/<path:filename>')
def serve_frame(filename):
    return send_from_directory(frame_cached_root, filename)

def extract_video_frames(file_path, auto_mode=True, fix_fps=30, fix_frames=10):
    print(f"--- Entering extract_video_frames ---")
    print(f"File path: {file_path}")
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"Error: 无法打开视频文件 at path: {file_path}")
        return None, None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    total_tokens = token_calculate(height, width)
    if total_tokens > frame_max_tokens:
        print(f"视频分辨率过大, 超过每帧最大Token数({frame_max_tokens})")
        return None, None
    
    max_frames = model_max_tokens // total_tokens
    
    prompt = [
        {
            "role": "user",
            "content": [
                {"video": [], "fps": None},
                {"text" : ""}
            ]
        }
    ]
    frames_path = []

    if auto_mode:
        if max_frames > total_frames:
            max_frames = total_frames
        new_fps = fps * max_frames / total_frames
        prompt[0]["content"][0]["fps"] = int(new_fps)

        for frame_idx in range(max_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx * (total_frames // max_frames))
            ret, frame = cap.read()
            if not ret:
                continue
            frame_file = f"frame_{frame_idx:04d}.jpg"
            frame_file_path = os.path.join(frame_cached_root, frame_file)
            cv2.imwrite(frame_file_path, frame)
            base64_image = encode_image(frame_file_path)
            prompt[0]["content"][0]["video"].append(f"data:image/jpeg;base64,{base64_image}")
            frames_path.append(frame_file_path)
    else:
        if fix_fps <= 0 or fix_frames <= 0:
            return None, None
        frames_per_second = math.ceil(fps / fix_fps) # Corrected calculation
        max_fix_frames = min(fix_frames, total_frames // frames_per_second)
        prompt[0]["content"][0]["fps"] = int(fix_fps)
        if max_fix_frames > max_frames:
            return None, None

        for frame_idx in range(max_fix_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx * frames_per_second)
            ret, frame = cap.read()
            if not ret:
                continue
            frame_file = f"frame_{frame_idx:04d}.jpg"
            frame_file_path = os.path.join(frame_cached_root, frame_file)
            cv2.imwrite(frame_file_path, frame)
            prompt[0]["content"][0]["video"].append(f"{frame_file_path}") # Changed to file path
            frames_path.append(frame_file_path)

    cap.release()
    return frames_path, prompt

@app.route('/run', methods=['POST'])
def run_inference():
    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({'error': 'Invalid prompt'}), 400

    def event_stream():
        responses = dashscope.MultiModalConversation.call(model='qvq-max', messages=prompt, stream=True, incremental_output=True)
        for response in responses:
            yield f"data: {json.dumps(response)}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    try:
        clear_cache()
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
