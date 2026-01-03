import os
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime

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

def _get_user_role(uid):
    try:
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('role', 'worker'), data
    except Exception:
        pass
    return 'worker', {}

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

# NOWY ENDPOINT: zapisywanie raportu do podkolekcji orders/<order_id>/reports
@app.route('/orders/<order_id>/report', methods=['POST'])
@require_firebase_token
def post_report(order_id):
    uid = request.firebase_user['uid']
    # pobierz profil użytkownika (jeśli istnieje)
    user_doc = db.collection('users').document(uid).get()
    user = user_doc.to_dict() if user_doc.exists else {}
    role = user.get('role', 'worker')

    order_ref = db.collection('orders').document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        return jsonify({"msg": "Zlecenie nie istnieje"}), 404
    order = order_doc.to_dict()

    # tylko admin lub przypisany wykonawca mogą dodać raport
    if role != 'admin' and order.get('assignedTo') != uid:
        return jsonify({"msg": "Brak uprawnień"}), 403

    payload = request.get_json() or {}
    text = payload.get('text')
    if not text or not str(text).strip():
        return jsonify({"msg": "Brakuje treści raportu"}), 400

    report = {
        'authorUid': uid,
        'authorName': user.get('displayName') or request.firebase_user.get('name'),
        'text': text,
        'created_at': firestore.SERVER_TIMESTAMP
    }

    write_result = order_ref.collection('reports').add(report)
    # Bezpieczne wydrukowanie id (różne wersje SDK)
    try:
        report_ref = write_result[1]
        report_id = report_ref.id
    except Exception:
        report_id = None

    return jsonify({"msg": "Zapisano raport", "id": report_id}), 201

# =========================
# ADMIN ENDPOINTS
# =========================

@app.route('/admin/orders/available', methods=['GET'])
@require_firebase_token
def admin_available_orders():
    uid = request.firebase_user['uid']
    role, _ = _get_user_role(uid)
    if role != 'admin':
        return jsonify({"msg": "Brak uprawnień"}), 403

    q = db.collection('orders') \
        .where('status', '==', 'open') \
        .where('assignedTo', '==', None) \
        .order_by('created_at', direction=firestore.Query.DESCENDING)
    docs = q.stream()
    orders = []
    for d in docs:
        data = d.to_dict()
        data['id'] = d.id
        orders.append(data)
    return jsonify(orders), 200

@app.route('/admin/orders/current', methods=['GET'])
@require_firebase_token
def admin_current_orders():
    uid = request.firebase_user['uid']
    role, _ = _get_user_role(uid)
    if role != 'admin':
        return jsonify({"msg": "Brak uprawnień"}), 403

    q = db.collection('orders').order_by('created_at', direction=firestore.Query.DESCENDING)
    docs = q.stream()
    orders = []
    for d in docs:
        data = d.to_dict()
        data['id'] = d.id
        assigned_uid = data.get('assignedTo')
        if assigned_uid:
            user_doc = db.collection('users').document(assigned_uid).get()
            if user_doc.exists:
                u = user_doc.to_dict()
                data['assignedUser'] = {
                    'uid': assigned_uid,
                    'displayName': u.get('displayName'),
                    'email': u.get('email'),
                    'trade': u.get('trade')
                }
            else:
                data['assignedUser'] = {'uid': assigned_uid}
        else:
            data['assignedUser'] = None
        orders.append(data)
    return jsonify(orders), 200

@app.route('/admin/orders', methods=['POST'])
@require_firebase_token
def admin_create_order():
    uid = request.firebase_user['uid']
    role, _ = _get_user_role(uid)
    if role != 'admin':
        return jsonify({"msg": "Brak uprawnień"}), 403

    payload = request.get_json() or {}
    title = payload.get('title')
    trade = payload.get('trade')
    if not title or not trade:
        return jsonify({"msg": "Brakuje title/trade"}), 400

    order = {
        'title': title,
        'description': payload.get('description'),
        'trade': trade,
        'status': payload.get('status', 'open'),
        'price': payload.get('price'),
        'location': payload.get('location'),
        'ownerUid': uid,
        'assignedTo': payload.get('assignedTo', None),
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    write_result = db.collection('orders').add(order)
    try:
        doc_ref = write_result[1]
        order_id = doc_ref.id
    except Exception:
        order_id = None
    return jsonify({"msg": "Utworzono zlecenie", "id": order_id}), 201

@app.route('/admin/users', methods=['POST'])
@require_firebase_token
def admin_create_user():
    uid = request.firebase_user['uid']
    role, _ = _get_user_role(uid)
    if role != 'admin':
        return jsonify({"msg": "Brak uprawnień"}), 403

    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    display_name = data.get('displayName', '')
    trade = data.get('trade', '')
    new_role = data.get('role', 'worker')

    if not email or not password:
        return jsonify({"msg": "Brakuje email/password"}), 400

    try:
        new_user = auth.create_user(email=email, password=password, display_name=display_name)
        # set custom claims if desired
        try:
            auth.set_custom_user_claims(new_user.uid, {'role': new_role})
        except Exception:
            pass
        profile = {
            'email': email,
            'displayName': display_name,
            'role': new_role,
            'trade': trade,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        db.collection('users').document(new_user.uid).set(profile, merge=True)
        return jsonify({"msg": "Utworzono użytkownika", "uid": new_user.uid}), 201
    except Exception as e:
        return jsonify({"msg": "Błąd tworzenia użytkownika", "error": str(e)}), 400

# NEW: admin endpoint to list reports for an order
@app.route('/admin/orders/<order_id>/reports', methods=['GET'])
@require_firebase_token
def admin_order_reports(order_id):
    uid = request.firebase_user['uid']
    role, _ = _get_user_role(uid)
    if role != 'admin':
        return jsonify({"msg": "Brak uprawnień"}), 403

    order_ref = db.collection('orders').document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        return jsonify({"msg": "Zlecenie nie istnieje"}), 404

    reports_q = order_ref.collection('reports').order_by('created_at', direction=firestore.Query.DESCENDING)
    docs = reports_q.stream()
    reports = []
    for d in docs:
        data = d.to_dict()
        # convert possible timestamp to ISO string
        ca = data.get('created_at')
        if ca is not None:
            try:
                # Timestamp-like object
                if hasattr(ca, 'to_datetime'):
                    data['created_at'] = ca.to_datetime().isoformat()
                elif isinstance(ca, datetime):
                    data['created_at'] = ca.isoformat()
                else:
                    data['created_at'] = str(ca)
            except Exception:
                data['created_at'] = str(ca)
        reports.append({
            'id': d.id,
            'data': data
        })
    return jsonify(reports), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)