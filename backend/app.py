import os
import json
import secrets
import threading
from flask import Flask, render_template, request, jsonify, Response, session, send_from_directory
from flask_cors import CORS
from dotenv import dotenv_values
import dashscope
import google.generativeai as genai
from PIL import Image
from database import init_db, db
from models import Conversation, Message
from routes.auth import auth_bp, login_required
from video_utils import extract_frame, crop_region, frame_to_base64, get_video_info
from sam3_service import SAM3Predictor

app = Flask(__name__)

# Load environment variables
config = dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))

# Configure secret key for sessions
app.config['SECRET_KEY'] = config.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Configure permanent session lifetime (30 days for "remember me")
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Enable CORS for frontend development with credentials support
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Initialize database
init_db(app)

# Register authentication blueprint
app.register_blueprint(auth_bp)

DASHSCOPE_API_KEY = config.get("DASHSCOPE_API_KEY")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")

if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY
else:
    print("DASHSCOPE_API_KEY not found in .env file. DashScope functionality may be limited.")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("GEMINI_API_KEY not found in .env file. Gemini functionality will be limited.")

# SAM 3 configuration
SAM3_SERVICE_URL = config.get("SAM3_SERVICE_URL", "http://localhost:8100")
SAM3_LOCAL = config.get("SAM3_LOCAL", "false").lower() == "true"

# Initialize SAM 3 predictor (mock mode when not local or CUDA unavailable)
sam3_predictor = SAM3Predictor(use_mock=not SAM3_LOCAL)


@app.route('/')
def index():
    return render_template('index.html')

# ==================== 对话历史 (Conversation History) API ====================

@app.route('/api/conversations', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def handle_conversations():
    if request.method == 'OPTIONS':
        return '', 204
        
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        # Fetch conversations for user, newest first
        convs = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).all()
        return jsonify([c.to_dict() for c in convs])
        
    elif request.method == 'POST':
        # Create a new conversation
        data = request.get_json() or {}
        title = data.get('title', 'New Analysis')
        
        new_conv = Conversation(user_id=user_id, title=title)
        db.session.add(new_conv)
        db.session.commit()
        return jsonify(new_conv.to_dict()), 201

@app.route('/api/conversations/<int:conv_id>', methods=['GET', 'DELETE', 'OPTIONS'])
@login_required
def handle_conversation_detail(conv_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    user_id = session.get('user_id')
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404
        
    if request.method == 'GET':
        messages = Message.query.filter_by(conversation_id=conv_id).order_by(Message.created_at.asc()).all()
        return jsonify({
            'conversation': conv.to_dict(),
            'messages': [m.to_dict() for m in messages]
        })
        
    elif request.method == 'DELETE':
        db.session.delete(conv)
        db.session.commit()
        return jsonify({'message': 'Conversation deleted successfully'})


@app.route('/api/run', methods=['POST', 'OPTIONS'])
@login_required
def run_inference():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    prompt_data = data.get('prompt')
    selected_model = data.get('model')

    print(f"DEBUG: run_inference called. Selected model: {selected_model}")
    print(f"DEBUG: Prompt data received: {prompt_data}")

    if not prompt_data or not selected_model:
        print("DEBUG: Invalid prompt or model received.")
        return jsonify({'error': 'Invalid prompt or model'}), 400

    # Extract conversation details
    conv_id = data.get('conversation_id')
    if not conv_id:
        return jsonify({'error': 'conversation_id is required'}), 400

    # Verify conversation belongs to user
    user_id = session.get('user_id')
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    media_filename = data.get('media_filename')

    # Save user message to database
    user_input = prompt_data[0]['content'][1]['text']
    user_msg = Message(
        conversation_id=conv_id,
        role='user',
        content=user_input,
        has_video=bool(media_filename),
        video_path=media_filename
    )
    db.session.add(user_msg)
    conv.updated_at = db.func.now()
    db.session.commit()

    print(f"DEBUG: User input: {user_input}")

    def event_stream():
        if selected_model == 'dashscope':
            print("DEBUG: DashScope model selected.")
            if not DASHSCOPE_API_KEY:
                print("DEBUG: DashScope API Key not configured.")
                yield f"data: {json.dumps({'text': 'Error: DashScope API Key not configured.'})}\n\n"
                return
            
            dashscope_messages = [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
            print(f"DEBUG: Calling DashScope with messages: {dashscope_messages}")
            responses = dashscope.Generation.call(model='qwen-plus-latest', messages=dashscope_messages, stream=True, incremental_output=True)
            for response in responses:
                print(f"DEBUG: DashScope response chunk: {response}")
                formatted_response = {
                    "output": {
                        "choices": [
                            {
                                "message": {
                                    "content": [
                                        {"text": response.output.text}
                                    ]
                                }
                            }
                        ]
                    }
                }
                yield f"data: {json.dumps(formatted_response)}\n\n"
        
        elif selected_model == 'gemini':
            print("DEBUG: Gemini model selected.")
            if not GEMINI_API_KEY:
                print("DEBUG: Gemini API Key not configured.")
                yield f"data: {json.dumps({'text': 'Error: Gemini API Key not configured.'})}\n\n"
                return
            
            try:
                uploaded_file = None
                
                # Enforce JSON template
                json_instruction = """
You are a PRTS Analysis Core. Analyze the video and the user prompt, then output your response EXACTLY in this raw JSON format without any markdown code blocks (no ```json):
{
  "license_plate": "String or N/A",
  "vehicle_color": "String or N/A",
  "violation_type": "String or N/A",
  "timestamp": "Time range or N/A",
  "analysis": "Detailed analysis string",
  "suggested_penalty": "Penalty suggestion string"
}
"""
                gemini_prompt = [json_instruction, "User Command: " + user_input]

                # Handle media upload to Gemini if present
                if media_filename:
                    media_path = os.path.join(UPLOAD_FOLDER, media_filename)
                    if os.path.exists(media_path):
                        yield f"data: {json.dumps({'status': 'uploading_media', 'text': '[System]: Uploading visual feed to remote analysis core...'})}\n\n"
                        try:
                            # Upload to Google
                            uploaded_file = genai.upload_file(path=media_path)
                            
                            # Wait for processing
                            yield f"data: {json.dumps({'status': 'processing_media', 'text': '[System]: Media uplink successful. Analyzing frames...'})}\n\n"
                            while uploaded_file.state.name == "PROCESSING":
                                import time
                                time.sleep(2)
                                uploaded_file = genai.get_file(uploaded_file.name)
                            
                            if uploaded_file.state.name == "FAILED":
                                yield f"data: {json.dumps({'text': '[System]: Error: Media processing failed on remote core.'})}\n\n"
                            else:
                                gemini_prompt.insert(0, uploaded_file)
                        except Exception as ve:
                            print(f"ERROR: Media upload failed: {ve}")
                            yield f"data: {json.dumps({'text': f'[System]: Media integration failed: {str(ve)}'})}\n\n"
                
                yield f"data: {json.dumps({'status': 'generating_text', 'text': ''})}\n\n"
                model = genai.GenerativeModel('gemini-3-flash-preview')
                response = model.generate_content(gemini_prompt, stream=True)
                accumulated_text = ""
                for chunk in response:
                    if chunk.text:
                        accumulated_text += chunk.text
                        formatted_response = {
                            "output": {
                                "choices": [
                                    {
                                        "message": {
                                            "content": [
                                                {"text": chunk.text}
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                        yield f"data: {json.dumps(formatted_response)}\n\n"
                    
                # Clean up uploaded video from Google's servers to save space
                if uploaded_file:
                    try:
                        genai.delete_file(uploaded_file.name)
                        print(f"DEBUG: Deleted temporary file {uploaded_file.name} from Google servers.")
                    except Exception as clean_err:
                        print(f"WARNING: Failed to delete file from Google servers: {clean_err}")

                # Save assistant message to Database after completely generated
                with app.app_context():
                    db_conv = Conversation.query.get(conv_id)
                    ai_msg = Message(
                        conversation_id=conv_id,
                        role='assistant',
                        content=accumulated_text
                    )
                    db.session.add(ai_msg)
                    if db_conv:
                        db_conv.updated_at = db.func.now()
                    db.session.commit()
                    
            except Exception as e:
                print(f"ERROR: Gemini run failed: {e}")
                yield f"data: {json.dumps({'text': f'Error: {str(e)}'})}\n\n"
        
        else:
            print("DEBUG: Invalid model selected.")
            yield f"data: {json.dumps({'text': 'Error: Invalid model selected.'})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')


# ==================== 违停分析相关 API ====================

# 视频上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/uploads/<path:filename>')
def serve_media(filename):
    """Serve uploaded media files to the frontend player"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/upload-media', methods=['POST', 'OPTIONS'])
@login_required
def upload_media():
    """媒体文件上传接口（支持图片和视频）"""
    if request.method == 'OPTIONS':
        return '', 204
    
    # 兼容前端传递的字段名
    file = request.files.get('media') or request.files.get('video')
    
    if not file:
        return jsonify({'error': '未找到上传文件'}), 400
    
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # 保存文件
    filename = f"{session.get('user_id', 'anonymous')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({
        'message': '文件上传成功',
        'filename': filename,
        'filepath': filepath
    })


@app.route('/api/analyze/sam3', methods=['POST', 'OPTIONS'])
@login_required
def analyze_sam3():
    """SAM 3 车辆分割追踪 + 违停判定"""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    video_name = data.get('video', '')

    print(f"DEBUG: SAM 3 analysis requested for video: {video_name}")

    def event_stream():
        video_path = os.path.join(UPLOAD_FOLDER, video_name)
        if not os.path.exists(video_path):
            yield f"data: {json.dumps({'error': f'视频文件不存在: {video_name}'})}\n\n"
            return

        info = get_video_info(video_path)
        if not info:
            yield f"data: {json.dumps({'error': '无法读取视频文件'})}\n\n"
            return

        init_msg = f'[SAM3]: 正在初始化模型... 视频时长 {info["duration_sec"]}s, {info["total_frames"]} 帧'
        yield f"data: {json.dumps({'status': 'sam3_init', 'text': init_msg})}\n\n"

        progress_state = {"last_reported": 0}
        progress_events = []

        def on_progress(current, total):
            pct = int(current / total * 100) if total > 0 else 0
            if pct - progress_state["last_reported"] >= 10:
                progress_state["last_reported"] = pct
                progress_events.append(pct)

        try:
            if SAM3_LOCAL:
                result = sam3_predictor.process_video(video_path, progress_callback=on_progress)
            else:
                import requests as req
                try:
                    health = req.get(f"{SAM3_SERVICE_URL}/health", timeout=5)
                    if health.status_code == 200:
                        with open(video_path, 'rb') as f:
                            resp = req.post(
                                f"{SAM3_SERVICE_URL}/segment-video",
                                files={'video': (video_name, f)},
                                timeout=300
                            )
                        result = resp.json()
                    else:
                        yield f"data: {json.dumps({'status': 'sam3_fallback', 'text': '[SAM3]: 远程服务不可用，使用本地 Mock 模式'})}\n\n"
                        result = sam3_predictor.process_video(video_path, progress_callback=on_progress)
                except (req.ConnectionError, req.Timeout):
                    yield f"data: {json.dumps({'status': 'sam3_fallback', 'text': '[SAM3]: 远程服务不可用，使用本地 Mock 模式'})}\n\n"
                    result = sam3_predictor.process_video(video_path, progress_callback=on_progress)

            if "error" in result:
                yield f"data: {json.dumps({'error': result['error']})}\n\n"
                return

            vehicle_count = len(result["vehicles"])
            yield f"data: {json.dumps({'status': 'sam3_tracking', 'text': f'[SAM3]: 追踪完成，检测到 {vehicle_count} 辆车辆'})}\n\n"

            # Build human-readable summary
            violations = [v for v in result["vehicles"] if v.get("is_violation")]
            non_violations = [v for v in result["vehicles"] if not v.get("is_violation")]

            summary_lines = [
                f"## SAM 3 车辆追踪分析结果\n",
                f"- 视频时长: {result['duration_sec']}s ({result['total_frames']} 帧, {result['fps']:.1f} FPS)",
                f"- 检测车辆数: {len(result['vehicles'])}",
                f"- 违停车辆数: {len(violations)}\n",
            ]

            if violations:
                summary_lines.append("### 违停车辆\n")
                for v in violations:
                    summary_lines.append(
                        f"- **车辆 {v['track_id']}** (类型: {v['class']}): "
                        f"{v.get('violation_reason', '违停')}"
                    )

            if non_violations:
                summary_lines.append("\n### 正常行驶车辆\n")
                for v in non_violations:
                    summary_lines.append(
                        f"- 车辆 {v['track_id']} (类型: {v['class']}): 正常行驶"
                    )

            summary_text = "\n".join(summary_lines)

            # Stream the summary text
            formatted_response = {
                "output": {
                    "choices": [{
                        "message": {
                            "content": [{"text": summary_text}]
                        }
                    }]
                },
                "sam3_data": result
            }
            yield f"data: {json.dumps(formatted_response)}\n\n"

            # Save SAM 3 results to file for downstream steps
            result_path = os.path.join(UPLOAD_FOLDER, f"{video_name}_sam3.json")
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False)

        except Exception as e:
            print(f"ERROR: SAM 3 analysis failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/analyze/qvq', methods=['POST', 'OPTIONS'])
@login_required
def analyze_qvq():
    """使用视觉模型识别违停车辆车牌号（基于 SAM 3 裁剪帧）"""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    video_name = data.get('video', '')
    sam3_results = data.get('sam3_results', None)

    print(f"DEBUG: QVQ analysis requested for video: {video_name}")

    def event_stream():
        if not DASHSCOPE_API_KEY:
            yield f"data: {json.dumps({'error': 'DashScope API Key 未配置'})}\n\n"
            return

        # Load SAM 3 results from file if not passed directly
        results = sam3_results
        if not results:
            result_path = os.path.join(UPLOAD_FOLDER, f"{video_name}_sam3.json")
            if os.path.exists(result_path):
                with open(result_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)

        if not results or not results.get("vehicles"):
            yield f"data: {json.dumps({'error': '未找到 SAM 3 分析结果，请先执行车辆追踪'})}\n\n"
            return

        violations = [v for v in results["vehicles"] if v.get("is_violation")]
        if not violations:
            formatted_response = {
                "output": {
                    "choices": [{
                        "message": {
                            "content": [{"text": "未检测到违停车辆，无需进行车牌识别。"}]
                        }
                    }]
                }
            }
            yield f"data: {json.dumps(formatted_response)}\n\n"
            return

        video_path = os.path.join(UPLOAD_FOLDER, video_name)
        all_plate_results = []

        for v in violations:
            track_id = v["track_id"]
            frame_idx = v["best_frame_index"]
            bbox = v["best_frame_bbox"]

            yield f"data: {json.dumps({'status': 'extracting', 'text': f'[QVQ]: 正在提取车辆 {track_id} 的帧画面...'})}\n\n"

            frame = extract_frame(video_path, frame_idx)
            if frame is None:
                all_plate_results.append(f"- 车辆 {track_id}: 帧提取失败")
                continue

            cropped = crop_region(frame, bbox)
            if cropped.size == 0:
                all_plate_results.append(f"- 车辆 {track_id}: 裁剪区域无效")
                continue

            img_base64 = frame_to_base64(cropped)

            yield f"data: {json.dumps({'status': 'recognizing', 'text': f'[QVQ]: 正在识别车辆 {track_id} 的车牌...'})}\n\n"

            try:
                messages = [{
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{img_base64}"},
                        {"text": "请识别这张图片中车辆的车牌号。只输出车牌号，如果无法识别请输出'无法识别'。"}
                    ]
                }]

                from dashscope import MultiModalConversation
                response = MultiModalConversation.call(
                    model='qwen-vl-max',
                    messages=messages,
                )

                if response and response.output:
                    plate_text = response.output.choices[0].message.content[0].get("text", "无法识别")
                else:
                    plate_text = "识别失败"

                all_plate_results.append(f"- 车辆 {track_id} (类型: {v['class']}): {plate_text.strip()}")

            except Exception as e:
                print(f"ERROR: QVQ recognition failed for track {track_id}: {e}")
                all_plate_results.append(f"- 车辆 {track_id}: 识别出错 ({str(e)[:50]})")

        result_text = "## 车牌识别结果\n\n" + "\n".join(all_plate_results)
        formatted_response = {
            "output": {
                "choices": [{
                    "message": {
                        "content": [{"text": result_text}]
                    }
                }]
            }
        }
        yield f"data: {json.dumps(formatted_response)}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/analyze/merge', methods=['POST', 'OPTIONS'])
@login_required
def analyze_merge():
    """调用 Qwen 合并 SAM 3 违停数据和车牌识别结果，生成最终报告"""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    sam3_text = data.get('sam3_result', '')
    qvq_text = data.get('qvq_result', '')

    print(f"DEBUG: Merge report requested")

    def event_stream():
        if not DASHSCOPE_API_KEY:
            yield f"data: {json.dumps({'error': 'API Key 未配置'})}\n\n"
            return

        try:
            prompt = f"""你是一个交通违停分析报告生成系统。请根据以下两部分分析结果，生成一份完整的违停检测报告。

## 第一部分：SAM 3 车辆追踪与违停判定结果
{sam3_text}

## 第二部分：车牌识别结果
{qvq_text}

请依次输出：
1. 违停车辆汇总（车牌号 + 车辆类型 + 违停时长）
2. 每辆违停车辆的详细违停原因（基于追踪数据中的位置变化判定）
3. 建议处罚（根据现行《中华人民共和国道路交通安全法》）

请确保格式清晰明确，逻辑性强，仅基于以上提供的数据进行输出，不要主观臆断。"""

            messages = [{"role": "user", "content": prompt}]
            responses = dashscope.Generation.call(
                model='qwen-max-latest',
                messages=messages,
                stream=True,
                incremental_output=True
            )

            for response in responses:
                if response.output and response.output.text:
                    formatted_response = {
                        "output": {
                            "choices": [{
                                "message": {
                                    "content": [{"text": response.output.text}]
                                }
                            }]
                        }
                    }
                    yield f"data: {json.dumps(formatted_response)}\n\n"
        except Exception as e:
            print(f"ERROR: Merge analysis failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def handle_settings():
    """获取或保存系统设置"""
    global DASHSCOPE_API_KEY, GEMINI_API_KEY
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    if request.method == 'POST':
        data = request.get_json()
        new_dashscope_key = data.get('dashscope_key')
        new_gemini_key = data.get('gemini_key')
        
        # 更新内存中的变量
        if new_dashscope_key:
            DASHSCOPE_API_KEY = new_dashscope_key
            dashscope.api_key = new_dashscope_key
            
        if new_gemini_key:
            GEMINI_API_KEY = new_gemini_key
            
        # 更新 .env 文件
        try:
            # 读取现有内容
            env_content = {}
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()
            
            # 更新值
            if new_dashscope_key:
                env_content['DASHSCOPE_API_KEY'] = new_dashscope_key
            if new_gemini_key:
                env_content['GEMINI_API_KEY'] = new_gemini_key
                
            # 写入文件
            with open(env_path, 'w', encoding='utf-8') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
                    
            # 保留其他非键值对行的逻辑比较复杂，这里简化为重新写入所有识别到的键值对
            # 如果需要保留注释，需要更复杂的解析，但作为简单的设置功能，这样足够了
            
            return jsonify({'message': '设置已保存'})
            
        except Exception as e:
            print(f"ERROR: Failed to save .env: {e}")
            return jsonify({'error': '保存设置失败'}), 500
            
    else:
        # GET 请求返回当前设置
        return jsonify({
            'dashscope_key': DASHSCOPE_API_KEY or '',
            'gemini_key': GEMINI_API_KEY or ''
        })


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

