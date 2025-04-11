from flask import Flask, render_template, request, jsonify
from redis_client import r
import uuid
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
#para jwt
app.config["SECRET_KEY"]= "supersecret"

SESSION_TIMEOUT = 60 * 30  # 30 minutes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    ip = request.remote_addr
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    # generamos el jwt
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT),
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    
    # guardamos el token como string