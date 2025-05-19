from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

@app.route('/echo', methods=['POST'])
def upload():
    data = request.get_json()
    message = data.get("message", "")
    
    chat = gemini_model.start_chat()
    response = chat.send_message(message + "(友達のように接して,メッセージはなるべく短く！)")
    response_text = response.text.replace("*", ",")
    
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
