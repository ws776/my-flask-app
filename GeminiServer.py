from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash')

# グローバルなチャットセッション
chat = gemini_model.start_chat()

@app.route('/echo', methods=['POST'])
def upload():
    data = request.get_json()
    message = data.get("message", "")
    
    response = chat.send_message(message + "(敬語使わないで)")
    response_text = response.text.replace("*", ",")
    
    return jsonify({"response": response_text})
