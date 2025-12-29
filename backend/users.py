# backend/users.py - skrypt tworzący użytkownika testowego i przykładowe zlecenie
import os
import sys
import firebase_admin
from firebase_admin import credentials, auth, firestore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT = os.path.join(BASE_DIR, 'serviceAccountKey.json')

if not os.path.exists(SERVICE_ACCOUNT):
    print("Brak pliku serviceAccountKey.json w katalogu backend/. Nie commituj klucza do repo.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Tworzymy użytkownika w Firebase Auth
email = "worker1@example.com"
password = "P@ssw0rd123"  # zmień na bezpieczne hasło
display_name = "Marek Murarz"
trade = "murarz"

try:
    user = auth.get_user_by_email(email)
    print("Użytkownik już istnieje, uid:", user.uid)
except auth.UserNotFoundError:
    user = auth.create_user(email=email, password=password, display_name=display_name)
    print("Utworzono użytkownika w Auth, uid:", user.uid)

# Opcjonalnie ustaw claim (np. role worker)
try:
    auth.set_custom_user_claims(user.uid, {'role': 'worker'})
except Exception:
    # nie przerywamy jeśli nie można ustawić claimów (np. ograniczenia środowiska)
    pass

# Tworzymy profil w Firestore - używamy displayName i trade
profile = {
    'email': email,
    'displayName': display_name,
    'role': 'worker',   # 'worker' lub 'admin'
    'trade': trade,
    'created_at': firestore.SERVER_TIMESTAMP
}
db.collection('users').document(user.uid).set(profile, merge=True)
print("Dodano profil users/{}".format(user.uid))

# Tworzymy przykładowe zlecenie w kolekcji orders
order = {
    'title': 'Naprawa muru - test',
    'description': 'Uszkodzona ściana, potrzeba murarza.',
    'trade': trade,
    'status': 'open',
    'price': 400,
    'location': 'Ulica Testowa 1',
    'ownerUid': user.uid,
    'assignedTo': None,
    'created_at': firestore.SERVER_TIMESTAMP,
    'updated_at': firestore.SERVER_TIMESTAMP,
    'tags': ['remont', 'pilne'],
    # opcjonalnie participants: [ownerUid] (może być przydatne)
    'participants': [user.uid],
}
write_result = db.collection('orders').add(order)
# add zwraca (write_result, doc_ref) w pythonowym SDK — bezpiecznie wydrukujemy id
try:
    doc_ref = write_result[1]
    print("Dodano zlecenie id:", doc_ref.id)
except Exception:
    print("Dodano zlecenie (id nieznane w tej wersji SDK).")