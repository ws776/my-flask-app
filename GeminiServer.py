from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from collections import deque

app = Flask(__name__)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

# セッションごとの履歴管理用辞書
# 履歴はdequeで最大6要素（ユーザー3発言 + AI3応答）
chat_sessions = {}

MAX_HISTORY = 6  # 3往復分

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    if session_id not in chat_sessions:
        chat_sessions[session_id] = deque(maxlen=MAX_HISTORY)

    history = chat_sessions[session_id]

    # ユーザー発言を履歴に追加
    history.append({"author": "user", "content": message})

    # チャットセッションを開始
    chat = gemini_model.start_chat()

    # 今回のメッセージだけ送信（履歴はAPI側で管理されているので渡さない）
    response = chat.send_message(message + "(敬語使わないで)")

    response_text = response.text.replace("*", ",")

    # AI応答も履歴に追加
    history.append({"author": "ai", "content": response_text})

    return jsonify({"response": response_text, "session_id": session_id})
