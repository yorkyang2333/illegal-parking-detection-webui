import os
import json
from flask import Flask, render_template, request, jsonify, Response
from dotenv import dotenv_values
import dashscope
from PIL import Image

app = Flask(__name__)

config = dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))

DASHSCOPE_API_KEY = config.get("DASHSCOPE_API_KEY")


if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY
else:
    print("DASHSCOPE_API_KEY not found in .env file. DashScope functionality may be limited.")


@app.route('/')
def index():
    return render_template('index.html')


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

    # Extract user input from the prompt_data
    user_input = prompt_data[0]['content'][1]['text']

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
        
        else:
            print("DEBUG: Invalid model selected.")
            yield f"data: {json.dumps({'text': 'Error: Invalid model selected.'})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
