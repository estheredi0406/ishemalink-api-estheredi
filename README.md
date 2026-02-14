# IshemaLink Logistics API 

A high-performance, modular backend API built with **Django REST Framework** for a Rwandan logistics company. This system manages hybrid logistics operations, handling both high-speed **Domestic Couriers** and complex **International Cross-Border Trade**.

## Key Features

### 1. Modular Architecture

The project is structured as a **Modular Monolith** to ensure scalability and separation of concerns:
* **`core/`**: Centralized Identity & Access Management (IAM).
* **`domestic/`**: High-frequency local logistics (Bikes/Buses).
* **`international/`**: Compliance-heavy cross-border trade (Trucks/Customs).

### 2. Rwanda-Specific Identity (KYC)

* **Custom User Model:** Replaces default Django users to support **Agents** and **Customers**.
* **Strict Validation:** Enforces Rwandan standards:
    * **Phone:** Must start with `+250` (Regex validated).
    * **NID:** Must be exactly 16 numeric digits.

### 3. Distinct Business Logic
* **Domestic:** Lightweight tracking (`origin`, `destination`, `status`).
* **International:** Enforces trade compliance. Shipments to **Kenya (KE)** are automatically rejected without a valid **TIN Number**.

---

## Performance Features (Async & Cache)

This API implements advanced performance patterns to handle high traffic.

### 1. Asynchronous Workers (Non-Blocking SMS)
We utilize Django's **Asynchronous Views** (`async def`) to handle slow network operations like sending SMS notifications without blocking the main server thread.

* **How it works:** When a shipment status is updated, the server uses `await asyncio.sleep(2)` to simulate the latency of an external SMS gateway (e.g., Twilio). Because this is awaited asynchronously, the server remains free to handle other user requests during this pause.

* **How to Verify:**
    1.  Create a shipment using `POST /api/domestic/shipments/`.
    2.  Update its status using the **Async Endpoint**: `POST /api/domestic/shipments/{id}/update/`.
    3.  The response returns immediately, while the SMS log appears in the terminal console after the simulated delay.

### 2. Caching Strategy (Memory-Based)
To reduce database load, we implement **Look-Aside Caching** using Django's `LocMemCache`.

* **How it works:** Tariff (Pricing) data rarely changes. When a user requests pricing, the system first checks the RAM (Cache).
    * **Cache Miss:** If empty, it queries the database, saves the result to RAM, and returns it.
    * **Cache Hit:** If found, it returns the RAM data instantly (0ms latency).
* **How to Verify:**
    1.  Open your browser Developer Tools (Network Tab).
    2.  Request `GET /api/domestic/pricing/tariffs/`.
    3.  **First Request:** Standard response time.
    4.  **Second Request:** Instant response. Look for the custom header **`X-Cache-Hit: TRUE`** in the response headers.

---

## Tech Stack

* **Language:** Python 3.x
* **Framework:** Django 5.x, Django REST Framework (DRF)
* **Database:** SQLite (Dev)
* **Documentation:** OpenAPI 3.0 / Swagger UI (`drf-spectacular`)
* **Async:** `asyncio`, `asgiref`

---

##  Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository
```bash
git clone (https://github.com/estheredi0406/ishemalink-api-estheredi )
cd IshemaLink-API-Esteredi
python -m venv venv
source venv/bin/scripts/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

## 2. Security config

SECRET_KEY=your_django_secret_key
ENCRYPTION_KEY=your_32_byte_base64_fernet_key
DEBUG=True

## 2. Database initialization 

python manage.py makemigrations
python manage.py migrate
# Create the admin account
python manage.py createsuperuser
# Optional: Load the demo logistics data
python manage.py shell < create_demo_data.py

## 3. CRun the server 
python manage.py runserver

Access the API Documentation at: http://127.0.0.1:8000/api/docs/


Security & Compliance Documentation

The full technical threat model, mitigation strategies, and Rwanda Data Protection Law compliance report can be found here:

[**Technical Security Documentation (Google Doc)**](https://docs.google.com/document/d/1XZAGbR5qsc0cXiguuvx8TvRJLVGMaQfOyZ1fCZ2eZnk/edit?usp=sharing)

*Note: This document details the architectural decisions made to protect citizen data and prevent unauthorized access. It also has the link to the demo video*


