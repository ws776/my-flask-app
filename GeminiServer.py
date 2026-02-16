from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import traceback
import logging

# ロギング設定: DEBUGレベルで詳細なログを出力
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# --- 1. サーバー起動時の設定とチェック ---

# APIキーの設定 (環境変数名から取得)
API_KEY = os.getenv("GEMINI_API_KEY") 
app.logger.debug(f"GEMINI_API_KEY present: {bool(API_KEY)}")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    # APIキーがない場合、警告を出す
    app.logger.warning("GEMINI_API_KEY is NOT set. API requests will likely fail with a 500 error.")

# モデルインスタンスを作成
try:
    gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    app.logger.debug("GenerativeModel created successfully.")
except Exception as e:
    app.logger.exception("Failed to create GenerativeModel at startup: %s", e)
    gemini_model = None

# グローバルなチャットセッションを作成 (セッションリセットの原因だが、元の構造を維持)
try:
    if gemini_model:
        chat = gemini_model.start_chat()
        app.logger.info("Global chat session started.")
    else:
        chat = None
except Exception as e:
    app.logger.exception("Failed to start global chat session.")
    chat = None


@app.route('/echo', methods=['POST'])
def upload():
    # --- 2. リクエスト処理ログとエラー特定 ---
    
    # モデルが初期化されていない場合は早期リターン
    if not gemini_model or not chat:
        app.logger.error("Request received but Gemini model/chat session is unavailable.")
        return jsonify({"error": "Server misconfiguration: model or chat unavailable"}), 500
    
    try:
        # 1. rawデータとJSONパースのログ (JSON崩壊エラー特定のため)
        raw = request.data
        app.logger.debug(f"raw request data: {raw!r}")
        data = request.get_json(silent=True)
        app.logger.debug(f"parsed json: {data!r}")

        if data is None:
            # JSONパースエラーの場合、400 Bad Requestを返す
            app.logger.error("Failed to parse JSON (Invalid JSON format from client).")
            return jsonify({"error": "Invalid JSON in request", "raw_data": raw.decode(errors='replace')}), 400

        message = data.get("message", "")
        app.logger.debug(f"message received: {message!r}")

        # 2. API通信の試行 (認証/通信エラー特定のため)
        try:
            # チャットセッションにメッセージを送信
            response = chat.send_message(message + "(敬語使わないで)")
            app.logger.debug("chat.send_message OK.")
            
            # 応答テキストを取得
            response_text = response.text if getattr(response, "text", None) else ""
            response_text = response_text.replace("*", ",")
            
        except Exception as e:
            # API通信失敗 (認証失敗などがここに入る)
            app.logger.exception("API chat.send_message failed.")
            traceback.print_exc()
            return jsonify({"error":"send_message failed, likely API key issue", "detail": str(e)}), 500

        # 3. 正常応答
        return jsonify({"response": response_text})

    except Exception as e:
        # 想定外の最終的なサーバーエラー
        app.logger.exception("Unhandled exception in /echo")
        traceback.print_exc()
        return jsonify({"error": "internal server error", "detail": str(e)}), 500

if __name__ == "__main__":
    # Render環境のポートとホストを使用
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)