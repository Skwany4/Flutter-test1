import os
import sys
import firebase_admin
from firebase_admin import credentials, auth, firestore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    print("Brak pliku serviceAccountKey.json w katalogu backend/. Nie commituj klucza do repo.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

email = "admin@example.com"
password = "admin123"  # ZMIEŃ na mocne hasło przed użyciem
display_name = "Administrator"
trade = ""  # Jeśli chcesz przypisać adminowi branżę, wpisz tu np. 'murarz' lub zostaw pusty

try:
    user = auth.get_user_by_email(email)
    print("Użytkownik już istnieje w Firebase Auth:", user.uid)
except auth.UserNotFoundError:
    user = auth.create_user(email=email, password=password, display_name=display_name)
    print("Utworzono użytkownika:", user.uid)

# ustawienie claimów admina
auth.set_custom_user_claims(user.uid, {'role': 'admin'})

# zapis profilu w Firestore - używamy spójnych pól: displayName i trade
doc_ref = db.collection('users').document(user.uid)
doc_ref.set({
    'email': email,
    'displayName': display_name,
    'role': 'admin',
    'trade': trade,
}, merge=True)

print("Admin gotowy. Email:", email)