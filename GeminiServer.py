from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# APIキーの設定
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# Gemini-2.0-flashモデルを使用
gemini_model = genai.GenerativeModel(model_name='gemini-2.0-flash')

# グローバルなチャットセッションを作成
chat = gemini_model.start_chat()

@app.route('/echo', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        message = data.get("message", "")

        # チャットセッションにメッセージを送信
        response = chat.send_message(message + "(敬語使わないで)")

        # 応答テキストを取得して不要な文字を置換
        response_text = response.text.replace("*", ",") if response.text else ""

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
