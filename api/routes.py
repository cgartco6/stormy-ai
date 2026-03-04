from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from stormy.core.ai_engine import AIEngine

app = Flask(__name__,
            template_folder='../web/templates',
            static_folder='../web/static')
CORS(app)

ai_engine = AIEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', request.remote_addr)
    context = data.get('context', '')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    response = ai_engine.generate_response(
        user_input,
        session_id=session_id,
        context=context,
        ip_address=ip_address
    )
    return jsonify({'response': response})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Stormy is ready to rumble!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
