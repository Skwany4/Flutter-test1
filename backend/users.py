# backend/create_user_and_order.py
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT = os.path.join(BASE_DIR, 'serviceAccountKey.json')

cred = credentials.Certificate(SERVICE_ACCOUNT)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Tworzymy użytkownika w Firebase Auth
email = "worker1@example.com"
password = "P@ssw0rd123"  # zmień
display_name = "Marek Murarz"

try:
    user = auth.get_user_by_email(email)
    print("Użytkownik już istnieje, uid:", user.uid)
except auth.UserNotFoundError:
    user = auth.create_user(email=email, password=password, display_name=display_name)
    print("Utworzono użytkownika w Auth, uid:", user.uid)

# Tworzymy profil w Firestore
profile = {
    'email': email,
    'displayName': display_name,
    'role': 'worker',   # 'worker' lub 'admin'
    'trade': 'murarz',
    'created_at': firestore.SERVER_TIMESTAMP
}
db.collection('users').document(user.uid).set(profile, merge=True)
print("Dodano profil users/{}".format(user.uid))

# Tworzymy przykładowe zlecenie w kolekcji orders
order = {
    'title': 'Naprawa muru - test',
    'description': 'Uszkodzona ściana, potrzeba murarza.',
    'trade': 'murarz',
    'status': 'open',
    'price': 400,
    'location': 'Ulica Testowa 1',
    'ownerUid': user.uid,   # możesz ustawić admina lub innego użytkownika
    'assignedTo': None,
    'created_at': firestore.SERVER_TIMESTAMP,
    'updated_at': firestore.SERVER_TIMESTAMP,
    'tags': ['remont', 'pilne']
}
doc_ref = db.collection('orders').add(order)
print("Dodano zlecenie id:", doc_ref[1].id)