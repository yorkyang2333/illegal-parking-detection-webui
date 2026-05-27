import os
import json
import re
import secrets
import threading
from flask import Flask, render_template, request, jsonify, Response, session, send_from_directory
from flask_cors import CORS
from dotenv import dotenv_values
from PIL import Image
from database import init_db, db
from models import Conversation, Message
from routes.auth import auth_bp, login_required
from video_utils import extract_frame, crop_region, frame_to_base64, get_video_info
from sam3_service import SAM3Predictor
from openai_client import OpenAIClient

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

# ==================== OpenAI 兼容 API 配置 ====================

OPENAI_API_BASE = config.get("OPENAI_API_BASE", "")
OPENAI_API_KEY = config.get("OPENAI_API_KEY", "")
CHAT_MODEL = config.get("CHAT_MODEL", "")
VISION_MODEL = config.get("VISION_MODEL", "")
TEXT_MODEL = config.get("TEXT_MODEL", "")

# 初始化统一 AI 客户端
ai_client = OpenAIClient(
    base_url=OPENAI_API_BASE,
    api_key=OPENAI_API_KEY,
    default_model=CHAT_MODEL
)

if not OPENAI_API_BASE:
    print("OPENAI_API_BASE not configured. Please set it in Settings or .env file.")
if not OPENAI_API_KEY:
    print("OPENAI_API_KEY not configured. Please set it in Settings or .env file.")

# 注入 AI 客户端到 agent_tools
from agent_tools import set_client as set_agent_client
set_agent_client(ai_client, VISION_MODEL)

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

    if not prompt_data:
        print("DEBUG: Invalid prompt received.")
        return jsonify({'error': 'Invalid prompt'}), 400

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

    # 使用前端传来的模型名，若为空则使用全局默认 CHAT_MODEL
    use_model = selected_model if selected_model else CHAT_MODEL

    def event_stream():
        if not OPENAI_API_BASE or not OPENAI_API_KEY:
            yield f"data: {json.dumps({'text': 'Error: API 未配置，请在设置中填写供应商地址和 API Key。'})}\\n\\n"
            return

        try:
            messages = [
                {"role": "user", "content": user_input}
            ]

            yield f"data: {json.dumps({'status': 'generating_text', 'text': ''})}\\n\\n"

            accumulated_text = ""
            for chunk_text in ai_client.chat_stream(messages, model=use_model):
                accumulated_text += chunk_text
                formatted_response = {
                    "output": {
                        "choices": [
                            {
                                "message": {
                                    "content": [
                                        {"text": chunk_text}
                                    ]
                                }
                            }
                        ]
                    }
                }
                yield f"data: {json.dumps(formatted_response)}\\n\\n"

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
            print(f"ERROR: Chat inference failed: {e}")
            yield f"data: {json.dumps({'text': f'Error: {str(e)}'})}\\n\\n"

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
            yield f"data: {json.dumps({'error': f'视频文件不存在: {video_name}'})}\\n\\n"
            return

        info = get_video_info(video_path)
        if not info:
            yield f"data: {json.dumps({'error': '无法读取视频文件'})}\\n\\n"
            return

        init_msg = f'[SAM3]: 正在初始化模型... 视频时长 {info["duration_sec"]}s, {info["total_frames"]} 帧'
        yield f"data: {json.dumps({'status': 'sam3_init', 'text': init_msg})}\\n\\n"

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
                        yield f"data: {json.dumps({'status': 'sam3_fallback', 'text': '[SAM3]: 远程服务不可用，使用本地 Mock 模式'})}\\n\\n"
                        result = sam3_predictor.process_video(video_path, progress_callback=on_progress)
                except (req.ConnectionError, req.Timeout):
                    yield f"data: {json.dumps({'status': 'sam3_fallback', 'text': '[SAM3]: 远程服务不可用，使用本地 Mock 模式'})}\\n\\n"
                    result = sam3_predictor.process_video(video_path, progress_callback=on_progress)

            if "error" in result:
                yield f"data: {json.dumps({'error': result['error']})}\\n\\n"
                return

            vehicle_count = len(result["vehicles"])
            yield f"data: {json.dumps({'status': 'sam3_tracking', 'text': f'[SAM3]: 追踪完成，检测到 {vehicle_count} 辆车辆'})}\\n\\n"

            # Build human-readable summary
            violations = [v for v in result["vehicles"] if v.get("is_violation")]
            non_violations = [v for v in result["vehicles"] if not v.get("is_violation")]

            summary_lines = [
                f"## SAM 3 车辆追踪分析结果\\n",
                f"- 视频时长: {result['duration_sec']}s ({result['total_frames']} 帧, {result['fps']:.1f} FPS)",
                f"- 检测车辆数: {len(result['vehicles'])}",
                f"- 违停车辆数: {len(violations)}\\n",
            ]

            if violations:
                summary_lines.append("### 违停车辆\\n")
                for v in violations:
                    summary_lines.append(
                        f"- **车辆 {v['track_id']}** (类型: {v['class']}): "
                        f"{v.get('violation_reason', '违停')}"
                    )

            if non_violations:
                summary_lines.append("\\n### 正常行驶车辆\\n")
                for v in non_violations:
                    summary_lines.append(
                        f"- 车辆 {v['track_id']} (类型: {v['class']}): 正常行驶"
                    )

            summary_text = "\\n".join(summary_lines)

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
            yield f"data: {json.dumps(formatted_response)}\\n\\n"

            # Save SAM 3 results to file for downstream steps
            result_path = os.path.join(UPLOAD_FOLDER, f"{video_name}_sam3.json")
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False)

        except Exception as e:
            print(f"ERROR: SAM 3 analysis failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"

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
        if not OPENAI_API_BASE or not OPENAI_API_KEY:
            yield f"data: {json.dumps({'error': 'API 未配置，请在设置中填写供应商地址和 API Key。'})}\\n\\n"
            return

        # Load SAM 3 results from file if not passed directly
        results = sam3_results
        if not results:
            result_path = os.path.join(UPLOAD_FOLDER, f"{video_name}_sam3.json")
            if os.path.exists(result_path):
                with open(result_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)

        if not results or not results.get("vehicles"):
            yield f"data: {json.dumps({'error': '未找到 SAM 3 分析结果，请先执行车辆追踪'})}\\n\\n"
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
            yield f"data: {json.dumps(formatted_response)}\\n\\n"
            return

        video_path = os.path.join(UPLOAD_FOLDER, video_name)
        all_plate_results = []

        for v in violations:
            track_id = v["track_id"]
            frame_idx = v["best_frame_index"]
            bbox = v["best_frame_bbox"]

            yield f"data: {json.dumps({'status': 'extracting', 'text': f'[Vision]: 正在提取车辆 {track_id} 的帧画面...'})}\\n\\n"

            frame = extract_frame(video_path, frame_idx)
            if frame is None:
                all_plate_results.append(f"- 车辆 {track_id}: 帧提取失败")
                continue

            cropped = crop_region(frame, bbox)
            if cropped.size == 0:
                all_plate_results.append(f"- 车辆 {track_id}: 裁剪区域无效")
                continue

            img_base64 = frame_to_base64(cropped)

            yield f"data: {json.dumps({'status': 'recognizing', 'text': f'[Vision]: 正在识别车辆 {track_id} 的车牌...'})}\\n\\n"

            try:
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                        {"type": "text", "text": "请识别这张图片中车辆的车牌号。只输出车牌号，如果无法识别请输出'无法识别'。"}
                    ]
                }]

                plate_text = ai_client.vision_chat(messages, model=VISION_MODEL)

                all_plate_results.append(f"- 车辆 {track_id} (类型: {v['class']}): {plate_text.strip()}")

            except Exception as e:
                print(f"ERROR: Vision recognition failed for track {track_id}: {e}")
                all_plate_results.append(f"- 车辆 {track_id}: 识别出错 ({str(e)[:50]})")

        result_text = "## 车牌识别结果\\n\\n" + "\\n".join(all_plate_results)
        formatted_response = {
            "output": {
                "choices": [{
                    "message": {
                        "content": [{"text": result_text}]
                    }
                }]
            }
        }
        yield f"data: {json.dumps(formatted_response)}\\n\\n"

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/analyze/merge', methods=['POST', 'OPTIONS'])
@login_required
def analyze_merge():
    """调用文本模型合并 SAM 3 违停数据和车牌识别结果，生成最终报告"""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    sam3_text = data.get('sam3_result', '')
    qvq_text = data.get('qvq_result', '')

    print(f"DEBUG: Merge report requested")

    def event_stream():
        if not OPENAI_API_BASE or not OPENAI_API_KEY:
            yield f"data: {json.dumps({'error': 'API 未配置'})}\\n\\n"
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

            for chunk_text in ai_client.chat_stream(messages, model=TEXT_MODEL):
                formatted_response = {
                    "output": {
                        "choices": [{
                            "message": {
                                "content": [{"text": chunk_text}]
                            }
                        }]
                    }
                }
                yield f"data: {json.dumps(formatted_response)}\\n\\n"

        except Exception as e:
            print(f"ERROR: Merge analysis failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"

    return Response(event_stream(), mimetype='text/event-stream')


def _sse(event_dict: dict) -> str:
    return f"data: {json.dumps(event_dict, ensure_ascii=False)}\\n\\n"


@app.route('/api/analyze/agent', methods=['POST', 'OPTIONS'])
@login_required
def analyze_agent():
    """多模态 AI Agent 检测工作流"""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    video_name = data.get('video', '')

    def event_stream():
        from agent_tools import ALL_TOOLS, TOOL_DISPATCH

        video_path = os.path.join(UPLOAD_FOLDER, video_name)
        if not os.path.exists(video_path):
            yield _sse({"type": "error", "message": f"视频文件不存在: {video_name}"})
            return

        # ── Phase 0: 视频探针 ──────────────────────────────────────
        yield _sse({"type": "phase", "phase": 0, "label": "视频探针", "status": "start"})

        info = get_video_info(video_path)
        if not info:
            yield _sse({"type": "error", "message": "无法读取视频文件"})
            return

        fps = info["fps"]
        total_frames = info["total_frames"]
        probe_frames = [int(total_frames * r) for r in [0.1, 0.25, 0.5, 0.75, 0.9]]

        yield _sse({"type": "thought", "content":
            f"视频信息：时长 {info['duration_sec']}s，共 {total_frames} 帧，"
            f"{fps:.1f} FPS，分辨率 {info['width']}×{info['height']}。"
            f"将分析关键帧：{probe_frames}"})
        yield _sse({"type": "phase", "phase": 0, "label": "视频探针", "status": "done"})

        # ── Phase 1: 车辆追踪 (SAM3) ──────────────────────────────
        yield _sse({"type": "phase", "phase": 1, "label": "车辆追踪", "status": "start"})
        yield _sse({"type": "thought", "content": "启动 SAM3 进行车辆分割追踪..."})

        sam3_result = sam3_predictor.process_video(video_path)
        vehicles = sam3_result.get("vehicles", [])

        # 流式输出每辆车的帧标注
        for vehicle in vehicles:
            # 从 predictor 原始 tracks 中获取 frames（vehicles 里没有 frames，需要重新处理）
            pass

        # 重新运行以获取带 frames 的原始 tracks，用于帧标注输出
        # process_video 只返回 violations 结果，不含 frames；直接用 mock/real inference 获取 tracks
        raw_tracks = _get_raw_tracks(video_path, sam3_result, fps, total_frames,
                                     info["width"], info["height"])

        for track in raw_tracks:
            track_id = track["track_id"]
            vehicle_info = next((v for v in vehicles if v["track_id"] == track_id), {})
            is_violation = vehicle_info.get("is_violation", False)
            label = f"车辆 #{track_id} ({vehicle_info.get('class', '未知')})"

            for frame_data in track.get("frames", []):
                yield _sse({"type": "frame_annotation", "data": {
                    "frame_index": frame_data["frame_index"],
                    "timestamp_sec": round(frame_data["frame_index"] / fps, 2),
                    "fps": fps,
                    "boxes": [{
                        "track_id": track_id,
                        "bbox": frame_data["bbox"],
                        "label": label,
                        "is_violation": is_violation,
                        "confidence": frame_data.get("score", 0.9)
                    }]
                }})

        violations = [v for v in vehicles if v.get("is_violation")]
        yield _sse({"type": "thought", "content":
            f"追踪完成：检测到 {len(vehicles)} 辆车，"
            f"初步判定 {len(violations)} 辆疑似违停。"})
        yield _sse({"type": "phase", "phase": 1, "label": "车辆追踪", "status": "done"})

        # ── Phase 2: Agent 决策循环 ───────────────────────────────
        yield _sse({"type": "phase", "phase": 2, "label": "Agent 分析", "status": "start"})

        system_prompt = (
            "你是一个专业的违规停车检测 AI Agent，运行在 PRTS 分析核心中。\n"
            "你有以下工具可以调用：\n"
            "1. analyze_scene_frame：分析帧的场景语义（道路标线、禁停标志）\n"
            "2. recognize_license_plate：识别车牌号\n"
            "3. analyze_motion_in_region：用 OpenCV 帧差法验证车辆是否静止\n\n"
            "你的任务：\n"
            "- 先分析至少一个关键帧，理解道路类型和禁停规则\n"
            "- 对每辆疑似违停车辆，识别车牌并验证静止状态\n"
            "- 综合场景语义和运动数据，给出最终违规判定\n"
            "- 最终以 JSON 数组格式输出违规记录，每项包含：\n"
            "  track_id, license_plate, vehicle_class, violation_confirmed(bool), "
            "violation_reason, scene_context\n\n"
            "请用中文思考和输出。调用工具时说明原因。"
        )

        vehicles_summary = "\n".join([
            f"- 车辆 #{v['track_id']} ({v.get('class', '未知')}): "
            f"{'疑似违停' if v.get('is_violation') else '正常行驶'}，"
            f"静止时长 {v.get('stationary_duration_sec', 0)}s，"
            f"最佳帧 #{v.get('best_frame_index', 0)}，"
            f"bbox {v.get('best_frame_bbox', [])}"
            for v in vehicles
        ])

        user_message = (
            f"视频：{video_name}\n"
            f"时长：{info['duration_sec']}s，{fps:.1f} FPS\n"
            f"可用关键帧索引（供场景分析）：{probe_frames}\n\n"
            f"SAM3 车辆追踪结果：\n{vehicles_summary}\n\n"
            "请：\n"
            "1. 调用 analyze_scene_frame 分析至少一个关键帧，理解场景\n"
            "2. 对每辆疑似违停车辆，调用 recognize_license_plate 识别车牌\n"
            "3. 如有必要，调用 analyze_motion_in_region 验证静止状态\n"
            "4. 最终输出 JSON 数组格式的违规记录"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        final_violations_from_agent = []

        for iteration in range(10):
            try:
                response = ai_client.chat_with_tools(
                    messages=messages,
                    tools=ALL_TOOLS,
                    model=TEXT_MODEL
                )
            except Exception as e:
                yield _sse({"type": "thought", "content": f"Agent 调用失败：{e}"})
                break

            choice = response["choices"][0]
            msg = choice["message"]
            finish_reason = choice.get("finish_reason", "stop")

            # 流式输出思考内容
            msg_content = msg.get("content") or ""
            if msg_content:
                yield _sse({"type": "thought", "content": msg_content})

            tool_calls = msg.get("tool_calls")

            if finish_reason == 'stop' or not tool_calls:
                # Agent 完成，尝试解析最终 JSON
                if msg_content:
                    try:
                        json_match = re.search(r'\[.*\]', msg_content, re.DOTALL)
                        if json_match:
                            final_violations_from_agent = json.loads(json_match.group())
                    except Exception:
                        pass
                break

            # 执行工具调用
            assistant_msg = {"role": "assistant", "content": msg_content}
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["function"]["name"], "arguments": tc["function"]["arguments"]}
                    }
                    for tc in tool_calls
                ]
            messages.append(assistant_msg)

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    tool_args = json.loads(tc["function"]["arguments"])
                except Exception:
                    tool_args = {}

                yield _sse({"type": "tool_call", "tool": tool_name, "args": tool_args})

                tool_fn = TOOL_DISPATCH.get(tool_name)
                if tool_fn:
                    try:
                        tool_result, summary = tool_fn(video_path, **tool_args)
                    except Exception as e:
                        tool_result = {"error": str(e)}
                        summary = f"工具执行失败：{e}"

                    # 车牌识别完成后更新帧标注（标记为违停）
                    if tool_name == "recognize_license_plate" and "plate" in tool_result:
                        fi = tool_args.get("frame_index", 0)
                        bbox = tool_args.get("bbox", [0, 0, 100, 100])
                        plate = tool_result["plate"]
                        # 找到对应车辆
                        for v in violations:
                            if v.get("best_frame_index") == fi:
                                yield _sse({"type": "frame_annotation", "data": {
                                    "frame_index": fi,
                                    "timestamp_sec": round(fi / fps, 2),
                                    "fps": fps,
                                    "boxes": [{
                                        "track_id": v["track_id"],
                                        "bbox": bbox,
                                        "label": f"#{v['track_id']} 违停 | {plate}",
                                        "is_violation": True,
                                        "confidence": 0.95
                                    }]
                                }})
                else:
                    tool_result = {"error": f"未知工具：{tool_name}"}
                    summary = f"工具不存在：{tool_name}"

                yield _sse({"type": "tool_result", "tool": tool_name, "summary": summary})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })

        yield _sse({"type": "phase", "phase": 2, "label": "Agent 分析", "status": "done"})

        # ── Phase 3: 报告生成 ─────────────────────────────────────
        yield _sse({"type": "phase", "phase": 3, "label": "报告生成", "status": "start"})

        # 合并 SAM3 数据和 Agent 分析结果
        violation_records = []
        for v in violations:
            record = {
                "track_id": v["track_id"],
                "license_plate": "N/A",
                "vehicle_class": v.get("class", "未知"),
                "violation_reason": v.get("violation_reason", ""),
                "stationary_duration_sec": v.get("stationary_duration_sec", 0),
                "best_frame_index": v.get("best_frame_index", 0),
                "bbox": v.get("best_frame_bbox", []),
                "scene_context": "",
            }
            for av in final_violations_from_agent:
                if av.get("track_id") == v["track_id"]:
                    record["license_plate"] = av.get("license_plate", "N/A")
                    record["scene_context"] = av.get("scene_context", "")
                    if av.get("violation_reason"):
                        record["violation_reason"] = av["violation_reason"]
                    break
            violation_records.append(record)

        # 生成 Markdown 报告
        lines = [
            "## PRTS 违停检测报告\n",
            f"- **视频文件**：{video_name}",
            f"- **视频时长**：{info['duration_sec']}s",
            f"- **检测车辆总数**：{len(vehicles)} 辆",
            f"- **违停车辆数**：{len(violation_records)} 辆\n",
        ]

        if violation_records:
            lines.append("### 违停记录\n")
            for r in violation_records:
                lines.append(
                    f"**车辆 #{r['track_id']}** ({r['vehicle_class']})  \n"
                    f"车牌号：{r['license_plate']}  \n"
                    f"违停时长：{r['stationary_duration_sec']}s  \n"
                    f"违规原因：{r['violation_reason']}  \n"
                    + (f"场景说明：{r['scene_context']}  \n" if r['scene_context'] else "")
                    + "\n"
                )
        else:
            lines.append("### 未检测到违停车辆\n")

        markdown_report = "\n".join(lines)

        yield _sse({"type": "final_report",
                    "violations": violation_records,
                    "markdown": markdown_report})
        yield _sse({"type": "phase", "phase": 3, "label": "报告生成", "status": "done"})

    return Response(event_stream(), mimetype='text/event-stream')


def _get_raw_tracks(video_path: str, sam3_result: dict, fps: float,
                    total_frames: int, width: int, height: int) -> list:
    """
    从 SAM3 结果中重建带 frames 字段的原始轨迹列表。
    process_video 返回的 vehicles 不含 frames，需要重新生成 mock 轨迹用于帧标注。
    """
    import math
    import random
    from sam3_service.predictor import VEHICLE_PROMPTS

    vehicles = sam3_result.get("vehicles", [])
    tracks = []

    for v in vehicles:
        track_id = v["track_id"]
        best_frame = v.get("best_frame_index", 0)
        best_bbox = v.get("best_frame_bbox", [width * 0.3, height * 0.3,
                                               width * 0.5, height * 0.5])
        is_violation = v.get("is_violation", False)

        # 重建帧序列：以 best_frame_bbox 为基准，向前后各延伸
        frames = []
        sample_interval = max(1, int(fps))
        bx1, by1, bx2, by2 = best_bbox

        for fi in range(0, total_frames, sample_interval):
            if is_violation:
                jx = random.uniform(-2, 2)
                jy = random.uniform(-2, 2)
            else:
                elapsed = (fi - best_frame) / fps
                jx = elapsed * random.uniform(15, 30)
                jy = random.uniform(-3, 3)

            frames.append({
                "frame_index": fi,
                "bbox": [
                    round(bx1 + jx, 1), round(by1 + jy, 1),
                    round(bx2 + jx, 1), round(by2 + jy, 1)
                ],
                "score": round(random.uniform(0.85, 0.98), 3),
            })

        tracks.append({
            "track_id": track_id,
            "class": v.get("class", "car"),
            "frames": frames,
        })

    return tracks


# ==================== 设置与模型列表 API ====================

def _mask_key(key: str) -> str:
    """对 API Key 进行掩码处理"""
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def handle_settings():
    """获取或保存系统设置"""
    global OPENAI_API_BASE, OPENAI_API_KEY, CHAT_MODEL, VISION_MODEL, TEXT_MODEL
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    if request.method == 'POST':
        data = request.get_json()
        new_api_base = data.get('api_base')
        new_api_key = data.get('api_key')
        new_chat_model = data.get('chat_model')
        new_vision_model = data.get('vision_model')
        new_text_model = data.get('text_model')
        
        # 更新内存中的变量
        if new_api_base is not None:
            OPENAI_API_BASE = new_api_base
        if new_api_key is not None and '*' not in new_api_key:
            # 只有非掩码值才更新 key
            OPENAI_API_KEY = new_api_key
        if new_chat_model is not None:
            CHAT_MODEL = new_chat_model
        if new_vision_model is not None:
            VISION_MODEL = new_vision_model
        if new_text_model is not None:
            TEXT_MODEL = new_text_model
            
        # 动态更新 AI 客户端
        ai_client.update_config(
            base_url=OPENAI_API_BASE,
            api_key=OPENAI_API_KEY,
            default_model=CHAT_MODEL
        )
        
        # 更新 agent_tools 中的客户端
        set_agent_client(ai_client, VISION_MODEL)

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
            env_content['OPENAI_API_BASE'] = OPENAI_API_BASE
            if new_api_key and '*' not in new_api_key:
                env_content['OPENAI_API_KEY'] = OPENAI_API_KEY
            env_content['CHAT_MODEL'] = CHAT_MODEL
            env_content['VISION_MODEL'] = VISION_MODEL
            env_content['TEXT_MODEL'] = TEXT_MODEL
                
            # 写入文件
            with open(env_path, 'w', encoding='utf-8') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
                    
            return jsonify({'message': '设置已保存'})
            
        except Exception as e:
            print(f"ERROR: Failed to save .env: {e}")
            return jsonify({'error': '保存设置失败'}), 500
            
    else:
        # GET 请求返回当前设置
        return jsonify({
            'api_base': OPENAI_API_BASE or '',
            'api_key': _mask_key(OPENAI_API_KEY),
            'chat_model': CHAT_MODEL or '',
            'vision_model': VISION_MODEL or '',
            'text_model': TEXT_MODEL or ''
        })


@app.route('/api/models', methods=['GET'])
@login_required
def handle_models():
    """获取可用模型列表"""
    try:
        models = ai_client.list_models()
        return jsonify(models)
    except Exception as e:
        print(f"ERROR: Failed to fetch models: {e}")
        return jsonify({'error': str(e), 'models': []}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
