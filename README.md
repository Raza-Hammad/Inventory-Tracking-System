
# Inventory Tracking System - Stage 3 Case Study

This project is a backend inventory tracking system built for the Bazaar Technologies Internship Case Study. The system starts with a simple inventory service for a single kiryana store and evolves into a scalable system supporting thousands of stores with authentication, logging, caching, and more.

## Technologies Used
- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Caching
- Flask-HTTPAuth
- Flask-Limiter

---

## Features Implemented

### Stage 1: Single Store Basic System
- Add Products and track quantity
- Handle stock-in, sales, and manual removal
- Local development with SQLite (initially)

### Stage 2: Multi-Store & PostgreSQL Upgrade
- PostgreSQL used instead of local storage
- Stores and Products are stored in their own tables
- Stocks are tracked per store using `Stock` table
- REST API built using Flask
- Basic Authentication added (admin/password123)
- Date-based filtering for stock movement reports

### Stage 3: Scalable, Production-Ready Features
- Asynchronous stock updates using Python `threading`
- Caching for inventory data using Flask-Caching
- Rate limiting with Flask-Limiter to prevent spam
- Stock movements are logged with timestamps for auditing

---

## Authentication
All endpoints (except DB creation) are protected using Basic Auth.
- **Username**: admin
- **Password**: password123

Use Postman or any HTTP client and add Basic Auth in the request headers.

---

## API Endpoints

### Add Store
```http
POST /store
{
  "name": "Malir Kiryana"
}
```

### Add Product
```http
POST /product
{
  "name": "Milk"
}
```

### Update Stock
```http
POST /stock
{
  "store_id": 1,
  "product_id": 1,
  "action": "stock-in",   // or "sale" or "remove"
  "amount": 50
}
```

### Get Inventory (cached)
```http
GET /inventory?store_id=1
```

### Get Stock Movements By Date
```http
GET /movements?store_id=1&start_date=2024-04-01&end_date=2024-04-12
```

---

## Design Decisions & Assumptions
- Started with SQLite for single-store then moved to PostgreSQL for scaling
- Each stock movement is saved with timestamp as audit log
- Asynchronous stock updates simulated using threading (in real app, would use message queue)
- Inventory API is cached per store to reduce DB hits
- Rate limiting added to protect APIs from abuse

---

## Scaling Plan
While I haven't deployed this to cloud, the system was designed with scale in mind:
- API is stateless and supports horizontal scaling
- Database can use read/write replica setup (writes to master, reads from slaves)
- Can be containerized using Docker and scaled via Kubernetes

---

## How to Run It
1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Start PostgreSQL and create a DB named `postgres`

3. Run the app:
```bash
python app.py
```

4. Use Postman to test the endpoints (don’t forget to add Basic Auth)

---

## Final Words
This system was designed to grow step by step while staying clean, testable, and secure. It covers all the main expectations of the case study — from local storage to scalable multi-store architecture with API protection and logging.

Thanks for reviewing!

— Muhammad Hammad Raza
