
# ⚡ Morph AI Engine

> **Real-Time Web Clickstream Pipeline, Star Schema Data Warehouse & Online/Offline Feature Store for Dynamic Web Personalization.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-Streams-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=flat&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

---

## 🎯 Overview

**Morph AI Engine** is an end-to-end Data Engineering platform designed to ingest high-throughput web clickstream events, transform raw unstructured telemetry into behavioral features, and serve low-latency contextual profiles (<30ms) to frontend applications for dynamic layout and CTA personalization.

### The Problem
Traditional web analytics tools (GA4, PostHog) are built for **post-hoc reporting**, not for **real-time decisioning**. On the other hand, standard client-side personalization breaks SEO, increases Cumulative Layout Shift (CLS), and lacks cross-session user intelligence.

### The Solution
A hybrid real-time + batch architecture:
1. **Real-time Path (Sub-50ms):** Stream-processed clickstream events calculating instant intent scores stored in an **In-Memory Feature Store (Redis)**.
2. **Batch Path (Analytical DW):** Persistent raw log storage transformed via **dbt** into a **Star Schema Data Warehouse (PostgreSQL)** for historical RFM (Recency, Frequency, Monetary) modeling, cohort aggregation, and offline features.

---

## 🏗️ Architecture

flowchart TD
    subgraph Client Layer
        A[Web Client / Frontend] -->|1. Async Event JSON| B[FastAPI Ingestion Engine]
        I[Frontend Decision Engine] <--|6. Get Feature Vector <30ms| H[Serving API]
    end

    subgraph Ingestion & Streaming
        B -->|2. Push Raw Event| C[(Redis Streams)]
        C -->|3. Consume Stream| D[Real-Time Feature Processor]
    end

    subgraph Storage & Feature Store
        D -->|4a. Update Real-Time Features| E[(Redis Online Feature Store)]
        D -->|4b. Append Persistent Raw Logs| F[(PostgreSQL Raw Data)]
    end

    subgraph Data Warehousing & Batch Layer
        F -->|5a. dbt Transformations| G[(PostgreSQL Star Schema DW)]
        G -->|5b. Backfill Offline Features| E
    end

    H <-->|Fetch Profile| E

```

---

## 🛠️ Tech Stack

| Domain | Technology | Purpose |
| --- | --- | --- |
| **Ingestion API** | **FastAPI + Pydantic v2** | Async HTTP ingestion endpoint with contract validation. |
| **Message Broker** | **Redis Streams** | Decouples event ingestion from feature calculation with zero data loss. |
| **Stream Processing** | **Python (Asyncio / Worker)** | Computes real-time engagement scores, intent classifiers, and dwell times. |
| **Online Feature Store** | **Redis Key-Value Cache** | Sub-30ms feature serving for edge/frontend rendering. |
| **Data Warehouse** | **PostgreSQL 16** | Relational OLAP storage structured in Star Schema (Fact & Dimension tables). |
| **Data Transformation** | **dbt-core** | Automated SQL modeling, lineage documentation, and data quality testing. |
| **Data Generation** | **Python (Faker / Async client)** | Synthetic multi-user traffic generator for benchmark testing. |
| **Containerization** | **Docker & Docker Compose** | One-command full local infrastructure orchestration. |

---

## 📐 Data Architecture & Modeling

### 1. Unified Event Schema (Ingestion Contract)

All inbound events strictly comply with the following JSON schema:

```json
{
  "event_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "session_id": "sess_889123",
  "user_id": "usr_400192",
  "timestamp": "2026-08-16T19:45:00.123Z",
  "event_type": "page_view", 
  "page_context": {
    "url": "[https://example.com/menu/wine-selection](https://example.com/menu/wine-selection)",
    "category": "beverages",
    "dwell_time_seconds": 38.5
  },
  "geo_context": {
    "country": "IT",
    "city": "Rome",
    "timezone": "Europe/Rome"
  },
  "device_context": {
    "device_type": "mobile",
    "user_agent": "Mozilla/5.0..."
  }
}

```

### 2. Star Schema Data Warehouse (dbt Models)

* **`fact_clickstream_events`**: Immutable event-level granular facts.
* **`fact_session_summary`**: Aggregated metrics per session (total duration, page count, conversion flag).
* **`dim_users`**: User profile, recency, frequency, total lifetime views, assigned cohort segment.
* **`dim_geo`**: Geographical dimension with country/city metadata.
* **`dim_pages`**: Page taxonomy, content categories, conversion weights.

---

## 🚀 Quickstart

### Prerequisites

* Docker & Docker Compose installed.
* Python 3.11+ (optional, for local script execution).

### 1. Spin up Infrastructure

Clone the repo and start all services via Docker:

```bash
git clone [https://github.com/Daddo172/morph-ai-data-engine.git](https://github.com/Daddo172/morph-ai-data-engine.git)
cd morph-ai-data-engine
docker compose up -d

```

This starts:

* **FastAPI Ingestion Service** at `http://localhost:8000`
* **Redis Instance** at `localhost:6379`
* **PostgreSQL Database** at `localhost:5432`
* **Real-time Feature Worker Process**
* **Serving API** at `http://localhost:8001`

### 2. Generate Synthetic Clickstream Traffic

Run the async traffic generator to simulate 100+ active user sessions:

```bash
python data/generate_traffic.py --users 50 --events-per-user 20

```

### 3. Run dbt Transformations & Data Quality Tests

Execute batch transformations to populate the Data Warehouse Star Schema:

```bash
docker compose exec dbt dbt run
docker compose exec dbt dbt test

```

### 4. Fetch Real-time Feature Vector

Query the Serving API for a user's calculated intent profile:

```bash
curl -X GET "http://localhost:8001/api/v1/features/usr_400192"

```

---

## 🔬 Feature Store Design

The feature store exposes two key feature groups:

| Feature Name | Type | Store | Computation Strategy | Description |
| --- | --- | --- | --- | --- |
| `intent_category` | Categorical | Online (Redis) | Real-time Stream | Category with highest dwell time in current session |
| `engagement_score` | Float (0.0-1.0) | Online (Redis) | Sliding Window (10m) | Weighted sum of clicks, scroll depth, and page views |
| `is_returning_visitor` | Boolean | Online + Offline | Batch (dbt) | True if total lifetime sessions > 1 |
| `rfm_segment` | String | Offline (PostgreSQL) | Daily Batch (dbt) | User RFM classification (e.g., *Champions*, *At Risk*) |

---

## 🧪 Testing & Data Quality

* **Unit & Integration Tests:** `pytest` suites covering FastAPI contracts, Redis consumer parsing, and Feature computation logic.
* **dbt Data Quality:** Schema assertions (`not_null`, `unique`, `relationships`) on all dimensional models.

---

## 🛣️ Implementation Roadmap

* [x] Phase 1: Architecture & Data Schema Specification
* [ ] Phase 2: Docker Compose Setup & Infrastructure Bootstrap
* [ ] Phase 3: FastAPI Ingestion Engine & Redis Streams Publisher
* [ ] Phase 4: Async Python Stream Consumer & Online Feature Store Logic
* [ ] Phase 5: PostgreSQL Storage & dbt Star Schema Transformations
* [ ] Phase 6: Fast Feature Serving API & Integration Benchmarks
* [ ] Phase 7: Synthetic Data Generator & GitHub Actions CI/CD Pipeline

---

## 👤 Author

**Davide Scolamiero**

* Software & Data Engineer | Founder at Complementors
* GitHub: [@Daddo172](https://www.google.com/search?q=https://github.com/Daddo172)

```
