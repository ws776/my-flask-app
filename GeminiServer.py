from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# 正しいモデル名に修正
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

# グローバルなチャットセッション
chat = gemini_model.start_chat()

@app.route('/echo', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        message = data.get("message", "")

        response = chat.send_message(message + "(敬語使わないで)")
        response_text = response.text.replace("*", ",") if response.text else ""

        return jsonify({"response": response_text})
    except Exception as e:
        # エラー内容を返す（開発用）
        return jsonify({"error": str(e)}), 500
