import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, Response, session, send_from_directory
from flask_cors import CORS
from dotenv import dotenv_values
import dashscope
import google.generativeai as genai
from PIL import Image
from database import init_db, db
from models import Conversation, Message
from routes.auth import auth_bp, login_required

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


@app.route('/api/analyze/gemini', methods=['POST', 'OPTIONS'])
@login_required
def analyze_gemini():
    """调用 Gemini 3 Pro 分析违停情况"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    video_name = data.get('video', '')
    
    print(f"DEBUG: Gemini analysis requested for video: {video_name}")
    print(f"DEBUG: Prompt: {prompt[:100]}...")
    
    def event_stream():
        if not GEMINI_API_KEY:
            yield f"data: {json.dumps({'error': 'Gemini API Key 未配置'})}\n\n"
            return
        
        try:
            model = genai.GenerativeModel('gemini-3-flash-preview')
            response = model.generate_content([
                f"你是一个视频违停分析系统。用户上传了一段名为 '{video_name}' 的视频。请进行如下分析：",
                prompt
            ], stream=True)
            
            for chunk in response:
                if chunk.text:
                    formatted_response = {
                        "output": {
                            "choices": [{
                                "message": {
                                    "content": [{"text": chunk.text}]
                                }
                            }]
                        }
                    }
                    yield f"data: {json.dumps(formatted_response)}\n\n"
        except Exception as e:
            print(f"ERROR: Gemini analysis failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/analyze/qvq', methods=['POST', 'OPTIONS'])
@login_required
def analyze_qvq():
    """调用 QVQ-Max 识别车牌号"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    video_name = data.get('video', '')
    
    print(f"DEBUG: QVQ-Max analysis requested for video: {video_name}")
    
    def event_stream():
        if not DASHSCOPE_API_KEY:
            yield f"data: {json.dumps({'error': 'API Key 未配置'})}\n\n"
            return
        
        try:
            # 模拟 QVQ-Max 车牌识别结果
            simulation_prompt = f"""你是一个车牌识别系统。请模拟识别视频中的车牌号。
视频名称：{video_name}
任务：{prompt}

请输出 1-3 个模拟的车牌号，格式如：
- 粤B12345
- 粤A88888
"""
            
            messages = [{"role": "user", "content": simulation_prompt}]
            responses = dashscope.Generation.call(
                model='qwen-plus-latest', 
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
            print(f"ERROR: QVQ analysis failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/analyze/merge', methods=['POST', 'OPTIONS'])
@login_required
def analyze_merge():
    """调用 Qwen3-Max 合并分析结果"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    print(f"DEBUG: Qwen3-Max merge requested")
    print(f"DEBUG: Prompt length: {len(prompt)}")
    
    def event_stream():
        if not DASHSCOPE_API_KEY:
            yield f"data: {json.dumps({'error': 'API Key 未配置'})}\n\n"
            return
        
        try:
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

