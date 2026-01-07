import os
import sys
import time
from typing import Dict, List

import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    print("Brak pliku serviceAccountKey.json.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =====================================================
# 20 ZLECEŃ – STATUS OPEN, OPIS >= 3 ZDANIA
# =====================================================
ORDERS: List[Dict] = [

    # ================= MURARZ (7) =================
    {
        "title": "Naprawa pęknięć elewacji",
        "trade": "murarz",
        "location": "Ulica Lipowa 8",
        "tags": ["elewacja"],
        "tools": ["kielnia", "szpachla", "grunt", "rusztowanie"],
        "description": (
            "Na elewacji budynku widoczne są pęknięcia oraz drobne ubytki tynku. "
            "Prace obejmują oczyszczenie uszkodzonych miejsc oraz ich uzupełnienie odpowiednią zaprawą. "
            "Całość powinna zostać zabezpieczona przed dalszym wpływem warunków atmosferycznych."
        ),
    },
    {
        "title": "Murowanie ścianki działowej",
        "trade": "murarz",
        "location": "Os. Zielone 15",
        "tags": ["konstrukcja"],
        "tools": ["poziomica", "kielnia", "mieszadło", "młotek"],
        "description": (
            "Zlecenie dotyczy wykonania ścianki działowej w lokalu mieszkalnym. "
            "Należy wymurować konstrukcję z pustaka oraz zachować pion i poziom na całej długości. "
            "Po zakończeniu ściana powinna być przygotowana pod dalsze prace wykończeniowe."
        ),
    },
    {
        "title": "Wyrównanie podłoża pod panele",
        "trade": "murarz",
        "location": "Ulica Długa 21",
        "tags": ["podłoga"],
        "tools": ["mieszadło", "wałek", "miarka"],
        "description": (
            "Podłoże w pomieszczeniu wymaga wyrównania przed montażem paneli. "
            "Prace obejmują przygotowanie powierzchni oraz wylanie masy samopoziomującej. "
            "Efektem ma być równa i stabilna powierzchnia gotowa do dalszych prac."
        ),
    },
    {
        "title": "Tynkowanie garażu",
        "trade": "murarz",
        "location": "Ulica Polna 11",
        "tags": ["tynk"],
        "tools": ["kielnia", "paca", "mieszadło"],
        "description": (
            "Ściany garażu wymagają położenia tynku wewnętrznego. "
            "Należy wyrównać powierzchnie oraz zadbać o estetyczne wykończenie narożników. "
            "Prace powinny zapewnić trwałość oraz odporność na wilgoć."
        ),
    },
    {
        "title": "Renowacja murka ogrodowego",
        "trade": "murarz",
        "location": "Ulica Ogrodowa 6",
        "tags": ["ogród"],
        "tools": ["szpachla", "cement", "pędzel"],
        "description": (
            "Murek ogrodowy posiada widoczne ubytki i spękania. "
            "Zadanie obejmuje naprawę uszkodzeń oraz wyrównanie powierzchni. "
            "Po zakończeniu murek powinien zostać zabezpieczony przed dalszą degradacją."
        ),
    },
    {
        "title": "Murowanie grilla ogrodowego",
        "trade": "murarz",
        "location": "Parkowa 2",
        "tags": ["ogród"],
        "tools": ["kielnia", "poziomica", "młotek"],
        "description": (
            "Zlecenie dotyczy budowy niewielkiego grilla ogrodowego. "
            "Konstrukcja powinna być wykonana z cegły oraz odporna na wysoką temperaturę. "
            "Należy zachować stabilność oraz estetykę wykonania."
        ),
    },
    {
        "title": "Naprawa schodów betonowych",
        "trade": "murarz",
        "location": "Ulica Leśna 3",
        "tags": [],
        "tools": ["szpachelka", "cement", "młotek"],
        "description": (
            "Schody betonowe posiadają ubytki oraz nierówności. "
            "Prace obejmują uzupełnienie uszkodzeń oraz wyrównanie stopni. "
            "Celem jest przywrócenie bezpieczeństwa i estetyki schodów."
        ),
    },

    # ================= ELEKTRYK (7) =================
    {
        "title": "Wymiana rozdzielnicy elektrycznej",
        "trade": "elektryk",
        "location": "Ulica Fabryczna 9",
        "tags": ["bezpieczeństwo"],
        "tools": ["śrubokręt izolowany", "miernik", "zaciskarka"],
        "description": (
            "Stara rozdzielnica wymaga wymiany na nową. "
            "Należy wykonać montaż zgodnie z obowiązującymi normami bezpieczeństwa. "
            "Po zakończeniu instalacja powinna zostać dokładnie sprawdzona."
        ),
    },
    {
        "title": "Montaż oświetlenia sufitowego",
        "trade": "elektryk",
        "location": "Os. Nowe 4",
        "tags": ["oświetlenie"],
        "tools": ["wkrętarka", "tester napięcia"],
        "description": (
            "Zlecenie obejmuje montaż kilku punktów oświetleniowych w salonie. "
            "Należy poprawnie podłączyć instalację oraz zamocować oprawy. "
            "Po wykonaniu wymagany jest test poprawności działania."
        ),
    },
    {
        "title": "Podłączenie piekarnika",
        "trade": "elektryk",
        "location": "Ulica Długa 9",
        "tags": ["AGD"],
        "tools": ["zaciskarka", "śrubokręt izolowany"],
        "description": (
            "Nowy piekarnik wymaga profesjonalnego podłączenia do instalacji. "
            "Prace obejmują sprawdzenie zabezpieczeń oraz poprawne podłączenie przewodów. "
            "Po zakończeniu należy przeprowadzić test bezpieczeństwa."
        ),
    },
    {
        "title": "Naprawa gniazdka elektrycznego",
        "trade": "elektryk",
        "location": "Ulica Krótka 1",
        "tags": [],
        "tools": ["tester napięcia", "śrubokręt"],
        "description": (
            "Jedno z gniazdek nie działa prawidłowo. "
            "Należy zdiagnozować przyczynę usterki i wykonać naprawę. "
            "Po zakończeniu wymagane jest sprawdzenie poprawności działania."
        ),
    },
    {
        "title": "Instalacja czujnika ruchu",
        "trade": "elektryk",
        "location": "Ulica Ogrodowa 14",
        "tags": ["smart"],
        "tools": ["wkrętarka", "miernik"],
        "description": (
            "Zlecenie polega na montażu czujnika ruchu do oświetlenia zewnętrznego. "
            "Należy prawidłowo podłączyć urządzenie oraz ustawić jego parametry. "
            "Po instalacji trzeba przetestować działanie systemu."
        ),
    },
    {
        "title": "Montaż gniazd USB",
        "trade": "elektryk",
        "location": "Ulica Lipowa 18",
        "tags": ["modernizacja"],
        "tools": ["śrubokręt", "tester napięcia"],
        "description": (
            "Standardowe gniazdka mają zostać zastąpione gniazdami z portami USB. "
            "Należy wykonać montaż zgodnie z zasadami bezpieczeństwa. "
            "Po zakończeniu instalacja powinna zostać sprawdzona."
        ),
    },
    {
        "title": "Przegląd instalacji elektrycznej",
        "trade": "elektryk",
        "location": "Rynek 5",
        "tags": ["przegląd"],
        "tools": ["miernik", "latarka"],
        "description": (
            "Zlecenie dotyczy kontroli instalacji elektrycznej w lokalu. "
            "Należy sprawdzić gniazdka, przewody oraz zabezpieczenia. "
            "Po przeglądzie wymagany jest krótki raport."
        ),
    },

    # ================= HYDRAULIK (6) =================
    {
        "title": "Wymiana zaworu głównego",
        "trade": "hydraulik",
        "location": "Ulica Słoneczna 7",
        "tags": ["pilne"],
        "tools": ["klucz nastawny", "taśma teflonowa"],
        "description": (
            "Zawór główny w instalacji wodnej wymaga wymiany. "
            "Należy przeprowadzić demontaż starego elementu i montaż nowego. "
            "Po zakończeniu instalacja powinna zostać sprawdzona pod kątem szczelności."
        ),
    },
    {
        "title": "Naprawa spłuczki",
        "trade": "hydraulik",
        "location": "Os. Zielone 9",
        "tags": [],
        "tools": ["klucz", "uszczelki"],
        "description": (
            "Spłuczka w toalecie nie działa poprawnie. "
            "Zadanie obejmuje wymianę uszkodzonych elementów mechanizmu. "
            "Po naprawie należy sprawdzić poprawność działania."
        ),
    },
    {
        "title": "Montaż kabiny prysznicowej",
        "trade": "hydraulik",
        "location": "Ulica Polna 22",
        "tags": ["łazienka"],
        "tools": ["wkrętarka", "poziomica", "silikon"],
        "description": (
            "Zlecenie dotyczy montażu kabiny prysznicowej w łazience. "
            "Należy poprawnie wykonać podłączenie odpływu oraz uszczelnienia. "
            "Po zakończeniu wymagany jest test szczelności."
        ),
    },
    {
        "title": "Odpowietrzenie instalacji grzewczej",
        "trade": "hydraulik",
        "location": "Ulica Leśna 19",
        "tags": ["ogrzewanie"],
        "tools": ["klucz do grzejników"],
        "description": (
            "Instalacja grzewcza wymaga odpowietrzenia. "
            "Należy sprawdzić wszystkie grzejniki w mieszkaniu. "
            "Po zakończeniu system powinien działać równomiernie."
        ),
    },
    {
        "title": "Wymiana syfonu",
        "trade": "hydraulik",
        "location": "Ulica Długa 30",
        "tags": [],
        "tools": ["klucz", "uszczelki"],
        "description": (
            "Syfon pod umywalką jest nieszczelny. "
            "Zadanie obejmuje jego wymianę oraz sprawdzenie połączeń. "
            "Po montażu należy wykonać test szczelności."
        ),
    },
    {
        "title": "Przegląd instalacji wodnej",
        "trade": "hydraulik",
        "location": "Ulica Miodowa 1",
        "tags": ["przegląd"],
        "tools": ["manometr", "latarka"],
        "description": (
            "Zlecenie dotyczy przeglądu instalacji wodnej w lokalu. "
            "Należy sprawdzić szczelność połączeń oraz ciśnienie. "
            "Po zakończeniu wymagane jest krótkie podsumowanie."
        ),
    },
]

# =====================================================

def seed():
    admin = db.collection("users").where("role", "==", "admin").limit(1).get()
    if not admin:
        print("Brak admina w kolekcji users.")
        return

    admin_uid = admin[0].id

    for i, od in enumerate(ORDERS):
        order = {
            "title": od["title"],
            "description": od["description"],
            "trade": od["trade"],
            "status": "open",
            "location": od["location"],
            "ownerUid": admin_uid,
            "assignedTo": None,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "tags": od["tags"],
            "tools": od["tools"],
            "participants": [admin_uid],
        }

        db.collection("orders").add(order)
        print(f"[{i+1}/20] Dodano: {order['title']}")
        time.sleep(0.05)

    print("✅ Dodano 20 zleceń (status=open).")

if __name__ == "__main__":
    seed()
