import os
import sys
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Ustalanie ścieżki absolutnej (zapewnia działanie niezależnie od katalogu wywołania)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    print("BŁĄD: Brak pliku serviceAccountKey.json. Nie commituj go do repozytorium.")
    sys.exit(1)

# Inicjalizacja Firebase (check zapobiega błędom przy ponownym ładowaniu)
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Konfiguracja admina
# TODO: W produkcji pobieraj hasło ze zmiennych środowiskowych (np. os.getenv)
email = "admin@example.com"
password = "admin123" 
display_name = "Administrator"
trade = "" 

try:
    # Sprawdzenie czy użytkownik już istnieje
    user = auth.get_user_by_email(email)
    print("Użytkownik już istnieje. UID:", user.uid)
except auth.UserNotFoundError:
    user = auth.create_user(email=email, password=password, display_name=display_name)
    print("Utworzono użytkownika. UID:", user.uid)

# Ustawienie Custom Claims (kluczowe dla reguł bezpieczeństwa Firestore)
auth.set_custom_user_claims(user.uid, {'role': 'admin'})

# Zapis/aktualizacja w Firestore (merge=True nie nadpisuje istniejących innych pól)
doc_ref = db.collection('users').document(user.uid)
doc_ref.set({
    'email': email,
    'displayName': display_name,
    'role': 'admin',
    'trade': trade,
}, merge=True)

print("Admin gotowy. Email:", email)