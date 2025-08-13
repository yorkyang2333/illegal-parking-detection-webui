import os
import cv2
import math
import json
import numpy as np
import base64
import shutil
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from dotenv import dotenv_values
import google.generativeai as genai
from PIL import Image
import dashscope

app = Flask(__name__)

config = dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))

DASHSCOPE_API_KEY = config.get("DASHSCOPE_API_KEY")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")

if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY
else:
    print("DASHSCOPE_API_KEY not found in .env file. DashScope functionality may be limited.")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("GEMINI_API_KEY not found in .env file. Gemini functionality may be limited.")

frame_cached_root = os.path.join(os.path.dirname(__file__), "frame_cache")
app.config['FRAME_CACHED_ROOT'] = frame_cached_root

if not os.path.exists(frame_cached_root):
    os.makedirs(frame_cached_root)

def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    # clear_cache() # Removed direct call, now handled by /clear_cache route
    if 'video' not in request.files:
        print("DEBUG: No video file in request.files")
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    video_path = os.path.join(frame_cached_root, video_file.filename)
    print(f"DEBUG: Saving video to: {video_path}")
    video_file.save(video_path)

    auto_mode = request.form.get('auto_mode', 'true').lower() == 'true'
    fix_fps = int(request.form.get('fps', 5))
    fix_frames = int(request.form.get('frames', 15))

    frames_path, prompt_from_extraction = extract_video_frames(video_path, auto_mode, fix_fps, fix_frames)

    print(f"DEBUG: frames_path from extraction: {frames_path}")
    print(f"DEBUG: prompt_from_extraction: {prompt_from_extraction}")

    if not frames_path:
        print("DEBUG: frames_path is empty or None, returning error")
        return jsonify({'error': 'Failed to process video'}), 500

    # Ensure the prompt structure is correct for the frontend
    # The frontend expects prompt[0].content[0].video to be the list of frame paths
    # and prompt[0].content[1].text to be the user input (which is empty initially)
    final_prompt_for_frontend = [
        {
            "role": "user",
            "content": [
                {"video": [os.path.basename(p) for p in frames_path]},
                {"text" : ""}
            ]
        }
    ]

    print(f"DEBUG: final_prompt_for_frontend: {final_prompt_for_frontend}")

    return jsonify({
        'frames_path': [os.path.basename(p) for p in frames_path],
        'prompt': final_prompt_for_frontend
    })

@app.route('/frames/<path:filename>')
def serve_frame(filename):
    return send_from_directory(frame_cached_root, filename)

def extract_video_frames(file_path, auto_mode=True, fix_fps=30, fix_frames=10):
    print(f"--- Entering extract_video_frames ---")
    print(f"File path: {file_path}")
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"DEBUG: Error: 无法打开视频文件 at path: {file_path}")
        return None, None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"DEBUG: Video properties - FPS: {fps}, Total Frames: {total_frames}, Width: {width}, Height: {height}")
    
    frames_path = []
    prompt = [
        {
            "role": "user",
            "content": [
                {"video": []},
                {"text" : ""}
            ]
        }
    ]

    if auto_mode:
        # For auto mode, we'll try to extract a reasonable number of frames
        # For simplicity, let's aim for max 15 frames evenly distributed
        target_frames = min(30, total_frames)
        if target_frames == 0: # Handle case of very short videos
            cap.release()
            print("DEBUG: target_frames is 0, returning empty lists")
            return [], []
        
        frame_interval = total_frames // target_frames
        if frame_interval == 0: # Ensure at least one frame is captured if video is very short
            frame_interval = 1

        print(f"DEBUG: Auto mode - Target Frames: {target_frames}, Frame Interval: {frame_interval}")

        for i in range(target_frames):
            frame_idx = i * frame_interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                print(f"DEBUG: Could not read frame at index {frame_idx}")
                continue
            frame_file = f"frame_{frame_idx:04d}.jpg"
            frame_file_path = os.path.join(frame_cached_root, frame_file)
            cv2.imwrite(frame_file_path, frame)
            frames_path.append(frame_file_path)
            print(f"DEBUG: Extracted frame: {frame_file_path}")
    else:
        if fix_fps <= 0 or fix_frames <= 0:
            print("DEBUG: fix_fps or fix_frames is <= 0, returning None, None")
            return None, None
        
        frames_per_second = math.ceil(fps / fix_fps)
        max_fix_frames = min(fix_frames, total_frames // frames_per_second)

        print(f"DEBUG: Manual mode - Frames per second: {frames_per_second}, Max Fix Frames: {max_fix_frames}")

        for frame_idx in range(max_fix_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx * frames_per_second)
            ret, frame = cap.read()
            if not ret:
                print(f"DEBUG: Could not read frame at index {frame_idx * frames_per_second}")
                continue
            frame_file = f"frame_{frame_idx:04d}.jpg"
            frame_file_path = os.path.join(frame_cached_root, frame_file)
            cv2.imwrite(frame_file_path, frame)
            frames_path.append(frame_file_path)
            print(f"DEBUG: Extracted frame: {frame_file_path}")

    cap.release()
    print(f"DEBUG: Finished extract_video_frames. Returning {len(frames_path)} frames.")
    return frames_path, prompt

@app.route('/run', methods=['POST'])
def run_inference():
    data = request.get_json()
    prompt_data = data.get('prompt')
    selected_model = data.get('model')

    print(f"DEBUG: run_inference called. Selected model: {selected_model}")
    print(f"DEBUG: Prompt data received: {prompt_data}")

    if not prompt_data or not selected_model:
        print("DEBUG: Invalid prompt or model received.")
        return jsonify({'error': 'Invalid prompt or model'}), 400

    # Extract user input and frames_path from the prompt_data
    user_input = prompt_data[0]['content'][1]['text']
    frames_path = []
    # The frames are now stored as file paths in the frontend's prompt structure
    # We need to extract them from the video field, which now contains file paths
    if 'video' in prompt_data[0]['content'][0]:
        frames_path = prompt_data[0]['content'][0]['video']

    print(f"DEBUG: User input: {user_input}")
    print(f"DEBUG: Frames paths: {frames_path}")

    def event_stream():
        if selected_model == 'dashscope':
            print("DEBUG: DashScope model selected.")
            if not DASHSCOPE_API_KEY:
                print("DEBUG: DashScope API Key not configured.")
                yield f"data: {json.dumps({'text': 'Error: DashScope API Key not configured.'})}\n\n"
                return
            # For DashScope, we need to convert image paths back to base64
            dashscope_prompt_content = []
            for frame_path_basename in frames_path:
                full_frame_path = os.path.join(frame_cached_root, frame_path_basename)
                dashscope_prompt_content.append({"image": encode_image_to_base64(full_frame_path)})
            dashscope_prompt_content.append({"text": user_input})

            dashscope_messages = [
                {
                    "role": "user",
                    "content": dashscope_prompt_content
                }
            ]
            print(f"DEBUG: Calling DashScope with messages: {dashscope_messages}")
            responses = dashscope.MultiModalConversation.call(model='qwen-vl-plus', messages=dashscope_messages, stream=True, incremental_output=True)
            for response in responses:
                print(f"DEBUG: DashScope response chunk: {response}")
                # DashScope response already has the expected structure
                yield f"data: {json.dumps(response)}\n\n"
        elif selected_model == 'gemini':
            print("DEBUG: Gemini model selected.")
            if not GEMINI_API_KEY:
                print("DEBUG: Gemini API Key not configured.")
                yield f"data: {json.dumps({'text': 'Error: Gemini API Key not configured.'})}\n\n"
                return
            
            gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            gemini_prompt_parts = []

            for frame_path_basename in frames_path:
                full_frame_path = os.path.join(frame_cached_root, frame_path_basename)
                try:
                    img = Image.open(full_frame_path)
                    gemini_prompt_parts.append(img)
                    print(f"DEBUG: Added image {full_frame_path} to Gemini prompt.")
                except Exception as e:
                    print(f"DEBUG: Error loading image {full_frame_path}: {e}")
                    continue
            
            gemini_prompt_parts.append(user_input)
            print(f"DEBUG: Calling Gemini with prompt parts: {gemini_prompt_parts}")
            responses = gemini_model.generate_content(gemini_prompt_parts, stream=True)
            for chunk in responses:
                print(f"DEBUG: Gemini response chunk: {chunk.text}")
                # Construct a response that mimics DashScope's structure for frontend compatibility
                formatted_response = {
                    "output": {
                        "choices": [
                            {
                                "message": {
                                    "content": [
                                        {"text": chunk.text.strip()}
                                    ]
                                }
                            }
                        ]
                    }
                }
                yield f"data: {json.dumps(formatted_response)}\n\n"
        else:
            print("DEBUG: Invalid model selected.")
            yield f"data: {json.dumps({'text': 'Error: Invalid model selected.'})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/clear_cache', methods=['POST'])
def clear_cache_route(): # Renamed function
    try:
        # Ensure the directory exists before trying to clear it
        if os.path.exists(app.config['FRAME_CACHED_ROOT']):
            shutil.rmtree(app.config['FRAME_CACHED_ROOT']) # Remove the directory and its contents
        os.makedirs(app.config['FRAME_CACHED_ROOT']) # Recreate the empty directory

        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
