import os
import sys
import time
import random
from typing import Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, auth, firestore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    print("Brak pliku serviceAccountKey.json w katalogu backend/. Nie commituj klucza do repo.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- konfiguracja użytkowników do utworzenia ---
# Hasła są testowe — zmień je przed użyciem w środowisku produkcyjnym.
USERS: List[Dict] = [
    {"email": "admin@example.com", "password": "admin", "displayName": "Administrator", "role": "admin", "trade": ""},
    {"email": "worker_murarz@example.com", "password": "worker", "displayName": "Marek Murarz", "role": "worker", "trade": "murarz"},
    {"email": "worker_murarz2@example.com", "password": "worker", "displayName": "Janek Murarz", "role": "worker", "trade": "murarz"},
    {"email": "worker_elektryk@example.com", "password": "worker", "displayName": "Piotr Elektryk", "role": "worker", "trade": "elektryk"},
    {"email": "worker_elektryk2@example.com", "password": "worker", "displayName": "Anna Elektryk", "role": "worker", "trade": "elektryk"},
    {"email": "worker_hydraulik@example.com", "password": "worker", "displayName": "Kasia Hydraulik", "role": "worker", "trade": "hydraulik"},
]

# --- przykładowe zlecenia (12) ---
ORDERS: List[Dict] = [
    {"title": "Naprawa muru przy wejściu", "description": "Spękania i ubytki", "trade": "murarz", "status": "open", "price": 500, "location": "Ulica Lipowa 5", "tags": ["remont"]},
    {"title": "Położenie płytek w łazience", "description": "Ok. 10m2", "trade": "murarz", "status": "open", "price": 800, "location": "Os. Zielone 12", "tags": ["glazura"]},
    {"title": "Instalacja gniazdka", "description": "Dodatkowe gniazdko w kuchni", "trade": "elektryk", "status": "open", "price": 120, "location": "Ulica Polna 9", "tags": ["bezpieczeństwo"]},
    {"title": "Naprawa instalacji wodnej", "description": "Cieknąca rura pod zlewem", "trade": "hydraulik", "status": "open", "price": 150, "location": "Ulica Słoneczna 3", "tags": ["pilne"]},
    {"title": "Wymiana stopnia schodów", "description": "Uszkodzony stopień", "trade": "murarz", "status": "assigned", "price": 200, "location": "Ulica Leśna 7", "tags": []},
    {"title": "Przegląd instalacji elektrycznej", "description": "Szybki przegląd przed wynajmem", "trade": "elektryk", "status": "assigned", "price": 250, "location": "Rynek 1", "tags": ["przegląd"]},
    {"title": "Uszczelnienie rury grzewczej", "description": "Nieszczelność przy reduktorze", "trade": "hydraulik", "status": "open", "price": 300, "location": "Ulica Miodowa 4", "tags": []},
    {"title": "Malowanie fragmentu ściany", "description": "Farbą zblendować nowy element", "trade": "murarz", "status": "closed", "price": 100, "location": "Os. Nowe 2", "tags": ["malowanie"]},
    {"title": "Podłączenie płyty indukcyjnej", "description": "Nowa płyta 3-fazowa", "trade": "elektryk", "status": "open", "price": 400, "location": "Ulica Fabryczna 10", "tags": ["AGD"]},
    {"title": "Wymiana baterii łazienkowej", "description": "Nowy model", "trade": "hydraulik", "status": "assigned", "price": 120, "location": "Ulica Długa 6", "tags": []},
    {"title": "Drobne prace murarskie - ławka", "description": "Naprawa zniszczonej ławki", "trade": "murarz", "status": "open", "price": 180, "location": "Park Centralny", "tags": []},
    {"title": "Podłączyć oświetlenie zewnętrzne", "description": "Oświetlenie na tarasie", "trade": "elektryk", "status": "assigned", "price": 220, "location": "Ulica Ogrodowa 2", "tags": []},
]


def create_or_get_user(u: Dict) -> Dict:
    """
    Returns a dict with keys: uid, email, displayName, role, trade
    """
    email = u["email"]
    try:
        fu = auth.get_user_by_email(email)
        uid = fu.uid
        print(f"Użytkownik istnieje: {email} (uid={uid})")
    except auth.UserNotFoundError:
        fu = auth.create_user(email=email, password=u["password"], display_name=u.get("displayName"))
        uid = fu.uid
        print(f"Utworzono użytkownika: {email} (uid={uid})")

    # spróbuj ustawić claimy (nie przerywamy w razie błędu)
    try:
        auth.set_custom_user_claims(uid, {"role": u.get("role", "worker")})
    except Exception as e:
        print("Nie udało się ustawić claimów:", e)

    # zapisz profil w Firestore
    profile = {
        "email": email,
        "displayName": u.get("displayName", ""),
        "role": u.get("role", "worker"),
        "trade": u.get("trade", ""),
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    db.collection("users").document(uid).set(profile, merge=True)
    return {"uid": uid, **profile}


def safe_add_order(order: Dict) -> Optional[str]:
    """
    Add order to Firestore and return the document id (best-effort).
    """
    try:
        res = db.collection("orders").add(order)
        # some SDK versions return (write_result, doc_ref) others return DocumentReference
        try:
            doc_ref = res[1]
            return doc_ref.id
        except Exception:
            try:
                return res.id  # DocumentReference
            except Exception:
                return None
    except Exception as e:
        print("Błąd przy dodawaniu zlecenia:", e)
        return None


def seed():
    print("Tworzę użytkowników...")
    email_to_user = {}
    for u in USERS:
        created = create_or_get_user(u)
        email_to_user[created["email"]] = created

    admin = email_to_user.get("admin@example.com")
    if not admin:
        print("Nie znaleziono admina po utworzeniu — przerywam.")
        return

    # lista workerów
    workers = [v for k, v in email_to_user.items() if v["role"] == "worker"]
    trade_map = {}
    for w in workers:
        t = w.get("trade") or ""
        trade_map.setdefault(t, []).append(w)

    print(f"Workerów: {len(workers)} -> {', '.join([w['displayName'] for w in workers])}")

    print("Tworzę zlecenia...")
    created_ids = []
    for i, od in enumerate(ORDERS):
        order = {
            "title": od["title"],
            "description": od.get("description", ""),
            "trade": od.get("trade", ""),
            "status": od.get("status", "open"),
            "price": od.get("price"),
            "location": od.get("location"),
            # ustaw ownerUid na admin (brak roli owner w systemie)
            "ownerUid": admin["uid"],
            "assignedTo": None,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "tags": od.get("tags", []),
            "participants": [admin["uid"]],
        }

        # jeśli status assigned -> przypisz worker-a z tej samej branży (jeśli jest)
        if order["status"] == "assigned":
            candidates = trade_map.get(order["trade"], [])
            if candidates:
                assigned = random.choice(candidates)
                order["assignedTo"] = assigned["uid"]
                order["participants"].append(assigned["uid"])
            else:
                # brak workerów tej branży -> ustaw status na open
                print(f"Brak workerów dla trade={order['trade']} -> ustawiam status=open dla '{order['title']}'")
                order["status"] = "open"

        doc_id = safe_add_order(order)
        created_ids.append(doc_id or "<unknown>")
        print(f"Dodano zlecenie: {order['title']} (id={doc_id})")
        time.sleep(0.05)

    print(f"Skończono. Dodano {len(created_ids)} zleceń.")
    print("Użytkownicy utworzeni i profile zapisane w kolekcji 'users'.")
    print("Zlecenia zapisane w kolekcji 'orders'.")


if __name__ == "__main__":
    seed()