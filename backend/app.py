import os
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')  # umieść tu swój plik

# Inicjalizacja Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

def require_firebase_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return jsonify({"msg": "Brak tokena"}), 401
        id_token = header.split(' ')[1]
        try:
            decoded = auth.verify_id_token(id_token)
        except Exception as e:
            return jsonify({"msg": "Nieprawidłowy token", "error": str(e)}), 401
        request.firebase_user = decoded
        return fn(*args, **kwargs)
    return wrapper

@app.route('/me', methods=['GET'])
@require_firebase_token
def me():
    uid = request.firebase_user['uid']
    doc = db.collection('users').document(uid).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    else:
        basic = {
            'uid': uid,
            'email': request.firebase_user.get('email'),
            'name': request.firebase_user.get('name'),
            'role': 'worker'
        }
        return jsonify(basic), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    trade = request.args.get('trade')
    status = request.args.get('status')
    q = db.collection('orders')
    if trade:
        q = q.where('trade', '==', trade)
    if status:
        q = q.where('status', '==', status)
    q = q.order_by('created_at', direction=firestore.Query.DESCENDING)
    docs = q.stream()
    orders = []
    for d in docs:
        data = d.to_dict()
        data['id'] = d.id
        orders.append(data)
    return jsonify(orders), 200

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    doc = db.collection('orders').document(order_id).get()
    if not doc.exists:
        return jsonify({"msg": "Zlecenie nie istnieje"}), 404
    data = doc.to_dict()
    data['id'] = doc.id
    return jsonify(data), 200

@app.route('/orders', methods=['POST'])
@require_firebase_token
def create_order():
    payload = request.get_json() or {}
    title = payload.get('title')
    trade = payload.get('trade')
    if not title or not trade:
        return jsonify({"msg": "Brakuje title/trade"}), 400
    uid = request.firebase_user['uid']
    order = {
        'title': title,
        'description': payload.get('description'),
        'trade': trade,
        'status': payload.get('status', 'open'),
        'price': payload.get('price'),
        'location': payload.get('location'),
        'ownerUid': uid,
        'assignedTo': None,
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    doc_ref = db.collection('orders').add(order)
    return jsonify({"id": doc_ref[1].id}), 201

@app.route('/orders/<order_id>/assign', methods=['POST'])
@require_firebase_token
def assign_order(order_id):
    uid = request.firebase_user['uid']
    user_doc = db.collection('users').document(uid).get()
    user = user_doc.to_dict() if user_doc.exists else {}
    role = user.get('role', 'worker')
    order_ref = db.collection('orders').document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        return jsonify({"msg": "Zlecenie nie istnieje"}), 404
    order = order_doc.to_dict()
    if role == 'worker':
        if user.get('trade') != order.get('trade'):
            return jsonify({"msg": "Branża nie pasuje"}), 403
        order_ref.update({
            'assignedTo': uid,
            'status': 'assigned',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"msg": "Przypisano użytkownika"}), 200
    elif role == 'admin':
        data = request.get_json() or {}
        worker_uid = data.get('worker_uid')
        if not worker_uid:
            return jsonify({"msg": "Brakuje worker_uid"}), 400
        order_ref.update({
            'assignedTo': worker_uid,
            'status': 'assigned',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"msg": "Przypisano wskazanego worker"}), 200
    return jsonify({"msg": "Brak uprawnień"}), 403

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)