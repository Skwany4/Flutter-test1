#!/usr/bin/env python3
# Skrypt narzędziowy: Sprawdza dokumenty w pod-kolekcji orders/<order_id>/reports
import sys
import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Helper: Serializacja obiektów Timestamp Firestore do stringa (ISO 8601)
# Biblioteka JSON nie obsługuje natywnie typów datetime/Timestamp
def ts_to_str(v):
    try:
        return v.to_datetime().isoformat()
    except Exception:
        return str(v)

def main():
    # Walidacja argumentów CLI (wymagany ID zlecenia)
    if len(sys.argv) < 2:
        print("Użycie: python check_reports.py <ORDER_ID> [path_to_service_account.json]")
        sys.exit(1)
    
    order_id = sys.argv[1]
    # Ustalanie ścieżki klucza względem lokalizacji skryptu (fallback)
    sa_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

    if not os.path.exists(sa_path):
        print("BŁĄD: Brak pliku serviceAccountKey.json pod ścieżką:", sa_path)
        sys.exit(2)

    # Inicjalizacja Firebase (check zapobiega podwójnej inicjalizacji)
    if not firebase_admin._apps:
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    order_ref = db.collection('orders').document(order_id)

    # Weryfikacja dokumentu nadrzędnego (Parent Document)
    if not order_ref.get().exists:
        print(f"Zlecenie {order_id} nie istnieje.")
        sys.exit(3)

    # Dostęp do sub-kolekcji (Subcollection) wewnątrz dokumentu
    reports_ref = order_ref.collection('reports').order_by('created_at', direction=firestore.Query.DESCENDING)
    
    # stream() pobiera dokumenty jeden po drugim (tu rzutujemy na listę)
    docs = list(reports_ref.stream())
    
    if not docs:
        print("Brak raportów dla zlecenia", order_id)
        return

    out = []
    for d in docs:
        data = d.to_dict()
        # Normalizacja daty przed zrzutem do JSON
        if 'created_at' in data:
            data['created_at'] = ts_to_str(data['created_at'])
        out.append({
            'id': d.id,
            'data': data
        })

    # ensure_ascii=False gwarantuje poprawne wyświetlanie polskich znaków w terminalu
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()