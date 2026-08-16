import time
import random
import uuid
import requests

API_URL = "http://127.0.0.1:8000/api/v1/event"

# Simulazione di utenti e pagine visitate
USERS = ["usr_roma_01", "usr_turista_02", "usr_wine_lover_03"]
CATEGORIES = ["menu", "carta_vini", "eventi", "prenotazione"]
CITIES = ["Roma", "Milano", "London", "New York"]

def run_simulation(num_events=15):
    print("🚀 Avvio simulazione traffico web per Morph AI Engine...\n")
    
    for i in range(num_events):
        user_id = random.choice(USERS)
        payload = {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": f"sess_{user_id}_1",
            "page_category": random.choice(CATEGORIES),
            "dwell_time_seconds": round(random.uniform(5.0, 60.0), 1),
            "city": random.choice(CITIES),
            "device": random.choice(["mobile", "desktop"])
        }
        
        try:
            res = requests.post(API_URL, json=payload)
            if res.status_code == 201:
                print(f"[{i+1}/{num_events}] Evento inviato -> Utente: {user_id} | Categoria: {payload['page_category']} ({payload['dwell_time_seconds']}s)")
            else:
                print(f"Errore invio: {res.status_code}")
        except Exception as e:
            print("⚠️ Errore di connessione! Assicurati che 'main.py' sia avviato con uvicorn.")
            break
            
        time.sleep(0.5)

    print("\n✅ Simulazione completata! Ora puoi interrogare /api/v1/profile/{user_id}")

if __name__ == "__main__":
    run_simulation()
