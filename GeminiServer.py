from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key='AIzaSyAZSJaKIpkme2RYbGnmNud6JA8sgr6Gn6Y')
model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
chat = model.start_chat()

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    message = data.get("message", "")
    response = chat.send_message(message + "(友達のように接して)")
    response_text = response.text    
        # アスタリスクをカンマに置き換え
    response_text = response_text.replace("*", ",")
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
