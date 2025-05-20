from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

chat_sessions = {}

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    if session_id not in chat_sessions:
        chat_sessions[session_id] = gemini_model.start_chat()

    chat = chat_sessions[session_id]

    try:
        response = chat.send_message(message + "(敬語使わないで)")
        print("AI応答:", response.text)
        response_text = response.text.replace("*", ",") if response.text else ""
    except Exception as e:
        print("send_messageでエラー:", e)
        return jsonify({"error": "AI応答の取得に失敗しました"}), 500

    return jsonify({"response": response_text, "session_id": session_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
