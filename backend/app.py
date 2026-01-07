#!/usr/bin/env python3
import os
import json
import logging
import traceback
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("backend")

# Ensure service account exists and read project_id for easier debugging
if not os.path.exists(SERVICE_ACCOUNT_PATH):
    logger.error("Brak pliku serviceAccountKey.json w katalogu backend/. Nie commituj klucza do repo.")
    raise SystemExit(1)

try:
    with open(SERVICE_ACCOUNT_PATH, 'r', encoding='utf-8') as f:
        sa_json = json.load(f)
        SA_PROJECT_ID = sa_json.get('project_id')
        logger.info("serviceAccount project_id: %s", SA_PROJECT_ID)
except Exception as e:
    logger.exception("Nie można wczytać serviceAccountKey.json: %s", e)
    raise

# Inicjalizacja Firebase Admin
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin zainicjalizowany")
    except Exception as e:
        logger.exception("Błąd inicjalizacji Firebase Admin: %s", e)
        raise

db = firestore.client()

app = Flask(__name__)
CORS(app)


def require_firebase_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        logger.debug("Incoming Authorization header: %s", header)
        if not header or not header.startswith('Bearer '):
            logger.warning("Missing or malformed Authorization header")
            return jsonify({"msg": "Brak tokena"}), 401
        id_token = header.split(' ', 1)[1]

        # Spróbujemy zweryfikować token z rosnącym clock_skew_seconds jeśli pojawi się błąd "used too early".
        # Kolejne wartości: 0 (domyślne) -> 5s -> 30s -> 120s
        skew_attempts = (0, 5, 30, 120)
        last_exception = None
        for skew in skew_attempts:
            try:
                # firebase_admin.auth.verify_id_token akceptuje param clock_skew_seconds
                decoded = auth.verify_id_token(id_token, clock_skew_seconds=skew)
                logger.debug("Decoded token uid=%s (clock_skew=%s)", decoded.get('uid'), skew)
                request.firebase_user = decoded
                return fn(*args, **kwargs)
            except Exception as e:
                last_exception = e
                msg = str(e).lower()
                logger.debug("verify_id_token failed (skew=%s): %s", skew, e)
                # jeśli to błąd związany z czasem ("used too early" lub wskazówki o clock skew) -> spróbuj z większym skew
                if ("used too early" in msg) or ("clock" in msg) or ("iat" in msg) or ("token used too early" in msg):
                    # spróbujemy następnego poziomu clock skew
                    continue
                else:
                    # inny błąd (np. wrong project, revoked) — nie próbujemy dalej
                    logger.error("Token verification failed (non-time error): %s", e)
                    logger.error(traceback.format_exc())
                    return jsonify({"msg": "Nieprawidłowy token", "error": str(e)}), 401

        # Jeżeli wszystkie próby się nie powiodły, zwróć ostatni błąd (zwykle "used too early" lub ogólny)
        logger.error("Token verification failed after clock skew attempts: %s", last_exception)
        logger.error(traceback.format_exc())
        return jsonify({
            "msg": "Nieprawidłowy token (failed after clock skew attempts)",
            "error": str(last_exception)
        }), 401
    return wrapper


def _get_user_role(uid):
    try:
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('role', 'worker'), data
    except Exception:
        logger.exception("Błąd przy pobieraniu roli użytkownika %s", uid)
    return 'worker', {}


@app.route('/_debug/sa_project', methods=['GET'])
def debug_sa_project():
    """
    Debug endpoint returning project_id read from serviceAccountKey.json.
    Useful to compare with the Firebase project your app uses.
    """
    return jsonify({"service_account_project_id": SA_PROJECT_ID}), 200


@app.route('/_debug/verify_token', methods=['POST'])
def debug_verify_token():
    """
    Debug endpoint to verify idToken via HTTP POST:
    { "token": "<ID_TOKEN>" }
    Returns decoded token or error message (useful from curl/postman).
    """
    data = request.get_json() or {}
    token = data.get('token')
    if not token:
        return jsonify({"msg": "Brakuje tokena w body (token)"}), 400
    try:
        decoded = auth.verify_id_token(token)
        return jsonify({"ok": True, "decoded": decoded}), 200
    except Exception as e:
        logger.error("Debug verify failed: %s", e)
        logger.error(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 401


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
        # check if there is at least one report
        try:
            reports = d.reference.collection('reports').limit(1).get()
            data['hasReports'] = len(reports) > 0
        except Exception:
            data['hasReports'] = False
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

        # check if there is at least one report for this order
        try:
            reports = d.reference.collection('reports').limit(1).get()
            data['hasReports'] = len(reports) > 0
        except Exception:
            data['hasReports'] = False

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

    # Parse tools: accept list or comma-separated string
    tools_payload = payload.get('tools', [])
    tools = []
    try:
        if isinstance(tools_payload, str):
            tools = [s.strip() for s in tools_payload.split(',') if s.strip()]
        elif isinstance(tools_payload, list):
            # ensure strings
            tools = [str(s).strip() for s in tools_payload if str(s).strip()]
        else:
            tools = []
    except Exception:
        tools = []

    order = {
        'title': title,
        'description': payload.get('description'),
        'trade': trade,
        'status': payload.get('status', 'open'),
        'price': payload.get('price'),
        'location': payload.get('location'),
        'ownerUid': uid,
        'assignedTo': payload.get('assignedTo', None),
        'tools': tools,
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
        try:
            auth.set_custom_user_claims(new_user.uid, {'role': new_role})
        except Exception:
            logger.warning("Nie udało się ustawić custom claims dla %s", new_user.uid)
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
        logger.exception("Błąd tworzenia użytkownika: %s", e)
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
        ca = data.get('created_at')
        if ca is not None:
            try:
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