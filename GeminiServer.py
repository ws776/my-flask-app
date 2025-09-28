from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# モデルを単発応答に変更（まずは動作確認優先）
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

@app.route('/echo', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        message = data.get("message", "")

        # まずは generate_content で動作確認
        response = gemini_model.generate_content(message + "(敬語使わないで)")
        response_text = response.text.replace("*", ",") if response.text else ""

        return jsonify({"response": response_text})
    except Exception as e:
        # エラー内容をそのまま返す
        return jsonify({"error": str(e)}), 500
