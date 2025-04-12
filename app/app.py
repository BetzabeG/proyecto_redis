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
    session_key = f"session:{token}"
    r.setex(session_key, SESSION_TIMEOUT, "active") #string para validar
    
    # guardamos el token como hash
    session_data_key = f"session_data:{token}"
    session_data ={
        "user_id": user_id,
        "ip_adress": ip,
        "last_activity": datetime.utcnow().isoformat(),
    }
    r.hset(session_data_key, mapping=session_data)
    r.expire(session_data_key, SESSION_TIMEOUT)
    
    return jsonify({"token": token})

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"error": "Fatal token"}), 401
    
    session_key = f"session:{token}"
    session_data_key = f"session_data:{token}"
    
    if not r.exists(session_key):
        return jsonify({"error": "Sesion expirada o invalida"}), 403
    
    try:
        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 403
    
    # aqui renovamos la expiracion del token
    r.expire(session_key, SESSION_TIMEOUT)
    r.expire(session_data_key, SESSION_TIMEOUT)
    
    session_info = r.hgetall(session_data_key)
    return jsonify({ "message": "Acceso permitido", "session_info": session_info })

@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    
    session_key = f"session:{token}"
    session_data_key = f"session_data:{token}"
    
    r.delete(session_key)
    r.delete(session_data_key)
    
    return jsonify({"message": "Logout successful"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")