# ⚡ Morph AI Engine

> **Proof of Concept: Real-Time Web Clickstream Pipeline, Data Warehouse & Feature Store for Dynamic Web Personalization.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=flat&logo=dbt&logoColor=white)](https://www.getdbt.com/)

---

## 🇮🇹 Presentazione del Progetto (Complementors)

Questo repository è un **Proof of Concept (PoC)** ideato e sviluppato dal fondatore di **Complementors** (partner digitale specializzato in Web Design, SEO/GEO avanzata, Data Engineering e AI applicata al business).

### Obiettivo del Progetto
Dimostrare l'architettura tecnica e la fattibilità di un **sito web adattivo**[cite: 1]: un ecosistema che non mostra la stessa identica esperienza a tutti gli utenti, ma decide quali contenuti, layout e Call-To-Action (CTA) mostrare in tempo reale basandosi sul contesto, la geolocalizzazione e il comportamento di navigazione[cite: 1].

L'obiettivo non è vendere la tecnologia in sé, ma **massimizzare il tasso di conversione (CRO) e le prenotazioni** dei clienti trasformando i dati di traffico anonimo in profili di intenzione d'acquisto[cite: 1].

---

## 🎯 Overview & Architecture

**Morph AI Engine** ingesta eventi clickstream ad alta frequenza, trasforma i log grezzi di navigazione in feature comportamentali e restituisce profili contestuali a bassa latenza per la personalizzazione dinamica del frontend[cite: 1].

### Il Flusso Dati (Data Pipeline)
1. **Event Tracking:** Il browser o il CMS (es. WordPress, Next.js) invia in modo asincrono un payload JSON con ogni interazione dell'utente (scroll, dwell time, pagina vista, contesto geo)[cite: 1].
2. **Ingestion Layer:** API ad alte prestazioni in **FastAPI** che valida lo schema dell'evento.
3. **Feature Engineering:** Calcolo dinamico degli score di intenzione (es. tempo speso su menu vs carta dei vini)[cite: 1].
4. **Feature Store:** Memorizzazione del profilo utente aggiornato per l'accesso immediato[cite: 1].
5. **Serving Layer:** Endpoint dedicato interrogato dal frontend per scambiare CTA o sezioni di pagina prima del rendering[cite: 1].

🛠️ Stack TecnologicoBackend Framework: FastAPI (Python 3.11+)  Validation & Data Contracts: Pydantic v2Storage (MVP): SQLite (zero-config per ambiente locale e test)Storage (Production Architecture): PostgreSQL / Redis / Supabase[cite: 1, 2]Data Transformation (Batch Layer): dbt-core (Star Schema Data Warehouse)  📐 Schema Dati & Profilazione1. Ingestion Event SchemaJSON{
  "event_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "user_id": "usr_roma_01",
  "session_id": "sess_889123",
  "page_category": "carta_vini",
  "dwell_time_seconds": 45.0,
  "city": "Roma",
  "device": "mobile"
}
2. Output Profile ResponseJSON{
  "user_id": "usr_roma_01",
  "is_known": true,
  "total_events": 5,
  "is_returning_visitor": true,
  "last_city": "Roma",
  "primary_interest": "carta_vini",
  "recommended_cta": "degustazione_vini_venerdi"
}
🚀 Quickstart (Esecuzione Locale)1. Clona il repository e installa le dipendenzeBashgit clone [https://github.com/Daddo172/morph-ai-engine.git](https://github.com/Daddo172/morph-ai-engine.git)
cd morph-ai-engine
pip install -r requirements.txt
2. Avvia l'Engine FastAPIBashuvicorn main:app --reload
L'API sarà attiva su http://127.0.0.1:8000. Puoi accedere alla documentazione Swagger automatica all'indirizzo http://127.0.0.1:8000/docs.3. Genera Traffico di ProvaIn un secondo terminale, esegui lo script di simulazione traffico:Bashpython generate_traffic.py
4. Interroga il Profilo CalcolatoBashcurl -X GET "[http://127.0.0.1:8000/api/v1/profile/usr_roma_01](http://127.0.0.1:8000/api/v1/profile/usr_roma_01)"
