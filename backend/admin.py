import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

email = "admin@example.com"
password = "admin123"  # ZMIEŃ na mocne hasło przed użyciem
display_name = "Administrator"

try:
    user = auth.get_user_by_email(email)
    print("Użytkownik już istnieje w Firebase Auth:", user.uid)
except auth.UserNotFoundError:
    user = auth.create_user(email=email, password=password, display_name=display_name)
    print("Utworzono użytkownika:", user.uid)

auth.set_custom_user_claims(user.uid, {'role': 'admin'})

doc_ref = db.collection('users').document(user.uid)
doc_ref.set({
    'email': email,
    'name': display_name,
    'role': 'admin'
}, merge=True)

print("Admin gotowy. Email:", email)