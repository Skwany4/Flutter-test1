import os
import sys
import time
import random
from typing import Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, auth, firestore
# Ustalanie ścieżki absolutnej (niezależność od CWD)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    print("Brak pliku serviceAccountKey.json w katalogu backend/. Nie commituj klucza do repo.")
    sys.exit(1)
# Singleton: inicjalizacja tylko jeśli aplikacja nie istnieje
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- DANE SEEDOWE ---
USERS: List[Dict] = [
    {"email": "admin@example.com", "password": "admin", "displayName": "Administrator", "role": "admin", "trade": ""},
    {"email": "worker_murarz@example.com", "password": "worker", "displayName": "Marek Murarz", "role": "worker", "trade": "murarz"},
    {"email": "worker_murarz2@example.com", "password": "worker", "displayName": "Janek Murarz", "role": "worker", "trade": "murarz"},
    {"email": "worker_elektryk@example.com", "password": "worker", "displayName": "Piotr Elektryk", "role": "worker", "trade": "elektryk"},
    {"email": "worker_elektryk2@example.com", "password": "worker", "displayName": "Anna Elektryk", "role": "worker", "trade": "elektryk"},
    {"email": "worker_hydraulik@example.com", "password": "worker", "displayName": "Kasia Hydraulik", "role": "worker", "trade": "hydraulik"},
]

# --- przykładowe zlecenia (13) ---
ORDERS: List[Dict] = [
    {
        "title": "Naprawa muru przy wejściu",
        "description": "Przy wejściu widać spękania i ubytki tynku, które pogłębiają się przy opadach. Potrzebne będzie oczyszczenie i uzupełnienie ubytków oraz wyrównanie powierzchni przed malowaniem. Praca powinna zapewnić długotrwałe zabezpieczenie przed dalszymi zniszczeniami.",
        "trade": "murarz",
        "status": "open",
        "location": "Ulica Lipowa 5",
        "tags": ["remont"],
        "tools": [" kielnia", "młotek", "mieszadło", "waga tynkowa"]
    },
    {
        "title": "Położenie płytek w łazience",
        "description": "Łazienka o powierzchni około 10m2 wymaga skucia starej okładziny oraz wyrównania podłoża. Następnie trzeba położyć nowe płytki i wykonać fugowanie z uszczelnieniem narożników. Zlecenie obejmuje również podstawowe prace wykończeniowe przy listwach i progach.",
        "trade": "murarz",
        "status": "open",
        "location": "Os. Zielone 12",
        "tags": ["glazura"],
        "tools": ["krzyżyki dystansowe", "szpachla", "miarka", "przecinarka do płytek"]
    },
    {
        "title": "Instalacja gniazdka",
        "description": "Należy doprowadzić nowy obwód do stanowiska w kuchni i zamontować dodatkowe gniazdko. Prace obejmują prowadzenie przewodów, montaż puszek i podłączenie zgodnie z normami. Po wykonaniu konieczny jest test bezpieczeństwa i poprawne oznakowanie obwodu.",
        "trade": "elektryk",
        "status": "open",
        "location": "Ulica Polna 9",
        "tags": ["bezpieczeństwo"],
        "tools": ["śrubokręt izolowany", "wkrętarka", "tester napięcia", "zaciskarka"]
    },
    {
        "title": "Naprawa instalacji wodnej",
        "description": "Cieknąca rura pod zlewem wymaga zlokalizowania przecieku i naprawy połączeń. Możliwe że konieczna będzie wymiana odcinka rury lub uszczelnień przy złączkach. Po naprawie przeprowadzony będzie test szczelności i krótki przegląd pozostałych przyłączy.",
        "trade": "hydraulik",
        "status": "open",
        "location": "Ulica Słoneczna 3",
        "tags": ["pilne"],
        "tools": ["klucz nastawny", "taśma teflonowa", "uszczelki", "nożyce do rur"]
    },
    {
        "title": "Wymiana stopnia schodów",
        "description": "Uszkodzony stopień schodów wymaga demontażu i wykonania nowego elementu. Trzeba dobrać odpowiedni materiał, zamocować go i wykończyć tak, aby dopasować do pozostałych stopni. Prace muszą zapewnić bezpieczne i stabilne użytkowanie schodów.",
        "trade": "murarz",
        "status": "assigned",
        "location": "Ulica Leśna 7",
        "tags": [],
        "tools": ["piła", "wkrętarka", "klin", "młotek"]
    },
    {
        "title": "Przegląd instalacji elektrycznej",
        "description": "Szybki przegląd instalacji przed wynajmem mieszkania obejmuje sprawdzenie gniazdek, przełączników i rozdzielnicy. Trzeba zweryfikować stan przewodów oraz działanie zabezpieczeń różnicowoprądowych. W razie wykrycia problemów wykonawca ma przygotować raport i propozycję naprawy.",
        "trade": "elektryk",
        "status": "assigned",
        "location": "Rynek 1",
        "tags": ["przegląd"],
        "tools": ["miernik elektryczny", "śrubokręt izolowany", "latarka", "zestaw bezpieczników"]
    },
    {
        "title": "Uszczelnienie rury grzewczej",
        "description": "W rejonie reduktora pojawiła się nieszczelność wymagająca szybkiej interwencji. Należy oczyścić miejsce, wymienić uszczelki lub odcinek rury oraz sprawdzić ciśnienie instalacji. Po naprawie potrzebny jest test działania i ewentualne odpowietrzenie układu.",
        "trade": "hydraulik",
        "status": "open",
        "location": "Ulica Miodowa 4",
        "tags": [],
        "tools": ["klucz rurkowy", "uszczelki", "taśma uszczelniająca", "manometr"]
    },
    {
        "title": "Malowanie fragmentu ściany",
        "description": "Trzeba zblendować nowy element malowany z resztą ściany, aby nie było widocznych przejść kolorystycznych. Prace obejmują przygotowanie powierzchni, gruntowanie i dwie warstwy farby. Zlecenie wymaga precyzji oraz ewentualnego dopasowania odcienia farby.",
        "trade": "murarz",
        "status": "closed",
        "location": "Os. Nowe 2",
        "tags": ["malowanie"],
        "tools": ["pędzle", "wałki", "folia ochronna", "szpachelka"]
    },
    {
        "title": "Podłączenie płyty indukcyjnej",
        "description": "Nowa płyta 3-fazowa wymaga profesjonalnego podłączenia do instalacji oraz sprawdzenia zabezpieczeń. Praca obejmuje wykonanie przyłącza, poprawne oznakowanie i testy obciążeniowe. Po montażu wykonawca zostawi krótką instrukcję bezpieczeństwa dla użytkownika.",
        "trade": "elektryk",
        "status": "open",
        "location": "Ulica Fabryczna 10",
        "tags": ["AGD"],
        "tools": ["kabel 3-fazowy", "zaciskarka", "wkrętarka", "tester obciążeniowy"]
    },
    {
        "title": "Wymiana baterii łazienkowej",
        "description": "Zlecenie obejmuje demontaż starej baterii i montaż nowego modelu zgodnie z instrukcją producenta. Trzeba sprawdzić uszczelnienia i ewentualnie wymienić elementy montażowe. Po montażu należy przetestować pracę baterii i sprawdzić szczelność połączeń.",
        "trade": "hydraulik",
        "status": "assigned",
        "location": "Ulica Długa 6",
        "tags": [],
        "tools": ["klucz nastawny", "uszczelki", "śrubokręt", "taśma teflonowa"]
    },
    {
        "title": "Drobne prace murarskie - ławka",
        "description": "Naprawa zniszczonej ławki wymaga oczyszczenia pęknięć i uzupełnienia brakujących fragmentów. Następnie trzeba wyrównać i zabezpieczyć powierzchnię przed warunkami atmosferycznymi. Praca powinna być wykonana tak, aby ławka była stabilna i estetyczna.",
        "trade": "murarz",
        "status": "open",
        "location": "Park Centralny",
        "tags": [],
        "tools": ["młotek", "szpachelka", "cement", "rusztowanie przestawne"]
    },
    {
        "title": "Podłączyć oświetlenie zewnętrzne",
        "description": "Zadanie polega na podłączeniu oświetlenia tarasu i zabezpieczeniu instalacji przed warunkami atmosferycznymi. Należy poprowadzić przewody, zamontować oprawy i wykonać odpowiednie uszczelnienia. Po instalacji wykonuje się test działania i montaż zabezpieczeń przeciwwilgociowych.",
        "trade": "elektryk",
        "status": "assigned",
        "location": "Ulica Ogrodowa 2",
        "tags": [],
        "tools": ["kabel outdoor", "uszczelki", "wkrętarka", "poziomica"]
    },
]

def create_or_get_user(u: Dict) -> Dict:

# Tworzy użytkownika w Auth i synchronizuje profil w Firestore.

    email = u["email"]
    try:
        #sprawdza czy istnieje, zamiast rzucać błędem
        fu = auth.get_user_by_email(email)
        uid = fu.uid
        print(f"Użytkownik istnieje: {email} (uid={uid})")
    except auth.UserNotFoundError:
        fu = auth.create_user(email=email, password=u["password"], display_name=u.get("displayName"))
        uid = fu.uid
        print(f"Utworzono użytkownika: {email} (uid={uid})")

# Custom Claims: kluczowe dla Security Rules (request.auth.token.role)
    try:
        auth.set_custom_user_claims(uid, {"role": u.get("role", "worker")})
    except Exception as e:
        print("Nie udało się ustawić claimów:", e)
# Profil w DB: merge=True zapobiega nadpisaniu innych pól (np. awatara, jeśli byłby dodany ręcznie)
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

# Wrapper na db.add(): obsługuje różnice w wersjach SDK Python (zwracanie tuple vs object).

    try:
        res = db.collection("orders").add(order)
# Python SDK v1 zwraca (write_result, doc_ref), v2 zwraca UpdateTime
        try:
            doc_ref = res[1] # tuple unpacking
            return doc_ref.id
        except Exception:
            try:
                return res.id  # DocumentReference
            except Exception:
                return None
    except Exception as e:
        print("Błąd przy dodawaniu zlecenia:", e)
        return None
# 1. Tworzenie kont i mapowanie email -> user_object

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
            "location": od.get("location"),
            # ustaw ownerUid na admin (brak roli owner w systemie)
            "ownerUid": admin["uid"],
            "assignedTo": None,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "tags": od.get("tags", []),
            "tools": od.get("tools", []),
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