from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import ffmpeg
import whisper

app = Flask(__name__)

# WhisperとGeminiの初期化
whisper_model = whisper.load_model("base")
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')


# Geminiへのメッセージ送信を関数化
def send_to_gemini(message: str) -> str:
    chat = gemini_model.start_chat()
    response = chat.send_message(message + "(友達のように接して)")
    return response.text.replace("*", ",")


# Flaskルート
@app.route('/echo', methods=['POST'])
def upload():
    if 'file' in request.files:
        audio_file = request.files['file']
        filename = "recorded.3gp"  # 固定ファイル名で保存
        filepath = os.path.join("/tmp", filename)
        audio_file.save(filepath)

        # .3gp → .wav 変換
        wav_path = os.path.join("/tmp", "output.wav")
        ffmpeg.input(filepath).output(wav_path).run(overwrite_output=True)

        # Whisperで文字起こし
        result = whisper_model.transcribe(wav_path)
        transcribed_text = result["text"]

        # Geminiで応答生成
        response_text = send_to_gemini(transcribed_text)
        return jsonify({"response": response_text})

    else:
        data = request.get_json()
        message = data.get("message", "")
        response_text = send_to_gemini(message)
        return jsonify({"response": response_text})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # RenderがPORT環境変数を渡してくる
    app.run(host='0.0.0.0', port=port)
