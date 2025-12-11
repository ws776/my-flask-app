from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import traceback
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# APIキーの設定（ログで確認）
API_KEY = os.getenv("GENAI_API_KEY")
app.logger.debug(f"GENAI_API_KEY present: {bool(API_KEY)}")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    app.logger.warning("GENAI_API_KEY is not set. Requests will likely fail.")

# モデルインスタンスは作っておく（start_chat は各リクエストで作る）
try:
    gemini_model = genai.GenerativeModel(model_name='gemini-2.0-flash')
    app.logger.debug("GenerativeModel created.")
except Exception as e:
    app.logger.exception("Failed to create GenerativeModel at startup: %s", e)
    gemini_model = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status":"ok", "model_present": gemini_model is not None}), 200

@app.route('/echo', methods=['POST'])
def upload():
    try:
        # 生データと JSON をログ
        raw = request.data
        app.logger.debug(f"raw request data: {raw!r}")
        data = request.get_json(silent=True)
        app.logger.debug(f"parsed json: {data!r}")

        if data is None:
            # クライアントにわかりやすく返す（開発環境向け）
            return jsonify({"error":"Invalid JSON in request", "raw": raw.decode(errors='replace')}), 400

        message = data.get("message", "")
        app.logger.debug(f"message received: {message!r}")

        if gemini_model is None:
            return jsonify({"error":"Server misconfiguration: model not initialized"}), 500

        # ここで個別の try/catch を入れて原因特定
        try:
            chat = gemini_model.start_chat()
            app.logger.debug("start_chat OK")
        except Exception as e:
            app.logger.exception("start_chat failed")
            traceback.print_exc()
            return jsonify({"error":"start_chat failed", "detail": str(e)}), 500

        try:
            # 必要であればメッセージを短くして試す（デバッグ用）
            response = chat.send_message(message + "(敬語使わないで)")
            app.logger.debug(f"raw response object: {response!r}")
            response_text = response.text if getattr(response, "text", None) else ""
            response_text = response_text.replace("*", ",")
        except Exception as e:
            app.logger.exception("chat.send_message failed")
            traceback.print_exc()
            return jsonify({"error":"send_message failed", "detail": str(e)}), 500

        return jsonify({"response": response_text})

    except Exception as e:
        # ここで最終的なスタックトレースを確認できる
        app.logger.exception("Unhandled exception in /echo")
        traceback.print_exc()
        return jsonify({"error": "internal server error", "detail": str(e)}), 500

if __name__ == "__main__":
    # 開発中は debug=True でも OK。production では debug=False
    app.run(host="0.0.0.0", port=5000, debug=True)
