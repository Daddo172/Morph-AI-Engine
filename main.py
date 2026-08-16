import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Inizializzazione App FastAPI
app = FastAPI(
    title="Morph AI - Data Engine MVP",
    description="Engine leggero per la profilazione comportamentale e la raccomandazione di CTA dinamiche.",
    version="1.0.0"
)

DB_FILE = "clickstream.db"

# 1. Inizializzazione Database SQLite
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clickstream_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            page_category TEXT NOT NULL,
            dwell_time_seconds REAL DEFAULT 0,
            city TEXT,
            device TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()


# 2. Schema Pydantic per Validazione Input
class WebEvent(BaseModel):
    event_id: str
    user_id: str
    session_id: str
    page_category: str  # es. 'menu', 'carta_vini', 'eventi', 'prenotazione'
    dwell_time_seconds: float = Field(default=0.0, ge=0)
    city: Optional[str] = "Roma"
    device: Optional[str] = "mobile"
    timestamp: Optional[str] = None


# 3. Endpoint Ingestion (Ricezione Dati)
@app.post("/api/v1/event", status_code=201)
def receive_event(event: WebEvent):
    ts = event.timestamp or datetime.utcnow().isoformat()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clickstream_events 
        (event_id, user_id, session_id, page_category, dwell_time_seconds, city, device, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.event_id,
        event.user_id,
        event.session_id,
        event.page_category,
        event.dwell_time_seconds,
        event.city,
        event.device,
        ts
    ))
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Evento registrato", "user_id": event.user_id}


# 4. Endpoint Feature Serving & Decision Logic (Profilazione)
@app.get("/api/v1/profile/{user_id}")
def get_user_profile(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Conteggio eventi totali e sessioni uniche
    cursor.execute("""
        SELECT COUNT(*), COUNT(DISTINCT session_id) 
        FROM clickstream_events 
        WHERE user_id = ?
    """, (user_id,))
    total_events, total_sessions = cursor.fetchone()

    # Utente mai visto prima
    if total_events == 0:
        conn.close()
        return {
            "user_id": user_id,
            "is_known": False,
            "primary_interest": "generico",
            "recommended_cta": "prenota_tavolo_standard"
        }

    # Calcolo categoria preferita in base al tempo di permanenza (dwell time)
    cursor.execute("""
        SELECT page_category, SUM(dwell_time_seconds) as total_dwell
        FROM clickstream_events
        WHERE user_id = ?
        GROUP BY page_category
        ORDER BY total_dwell DESC
        LIMIT 1
    """, (user_id,))
    top_cat_row = cursor.fetchone()
    primary_interest = top_cat_row[0] if top_cat_row else "generico"

    # Recupero ultima città rilevata
    cursor.execute("""
        SELECT city FROM clickstream_events
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    city_row = cursor.fetchone()
    last_city = city_row[0] if city_row else "Roma"

    conn.close()

    # Business Rules per l'assegnazione della CTA dinamica
    recommended_cta = "prenota_tavolo_standard"
    if primary_interest == "carta_vini":
        recommended_cta = "degustazione_vini_venerdi"
    elif primary_interest == "menu":
        recommended_cta = "whatsapp_menu_pranzo"
    elif primary_interest == "eventi":
        recommended_cta = "pass_privato_eventi"

    return {
        "user_id": user_id,
        "is_known": True,
        "total_events": total_events,
        "total_sessions": total_sessions,
        "is_returning_visitor": total_sessions > 1,
        "last_city": last_city,
        "primary_interest": primary_interest,
        "recommended_cta": recommended_cta
    }
