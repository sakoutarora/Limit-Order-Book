# 🚀 Trading Gateway API

A **RESTful + WebSocket API** for managing **orders, trades, and market data** in a trading system.  
Built with **FastAPI** for the REST layer and **gRPC** for high-performance backend communication.

---

## 🧭 Overview

This project provides:
- A **REST API** for submitting, modifying, and canceling orders.
- A **WebSocket service** for real-time updates on trades and order status.
- A **polling system** for streaming market data updates (Limit Order Book).

The backend integrates with a **gRPC service**, **Redis**, and supports **Docker-based deployment**.

---

## 📁 Project StructureProject Structure
api/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── orders.py
│   │   │   ├── trades.py
│   │   │   ├── websocket.py
│   │   ├── core/
│   │   │   ├── grpc_client.py
│   │   │   ├── redis.py
│   │   ├── tasks/
│   │   │   ├── poller.py
│   │   │   ├── trades.py
│   │   ├── models/
│   │   │   ├── order.py
│   │   │   ├── trade.py
│   ├── proto/
│   │   ├── lob.proto
│   ├── settings.py
├── requirements.txt
├── Dockerfile
├── README.md
---

## ✨ Features

✅ **Order Management** — Submit, modify, and cancel orders via REST.  
✅ **Trade Updates** — Get live updates through WebSocket streams.  
✅ **Market Data Polling** — Fetch and broadcast Limit Order Book (LOB) snapshots.  
✅ **gRPC Integration** — High-speed communication with matching engine.  
✅ **Docker Ready** — Easily containerized and deployable.

---

## ⚙️ Setup & Installation

### 🔧 Prerequisites
- **Python 3.8+**
- **Docker**
- (Optional) `protoc` compiler for gRPC

---

### 📥 Clone the Repository
```bash
git clone git@github.com:sakoutarora/Limit-Order-Book.git
cd trading-gateway-api

### 📦 Install Dependencies
pip install -r requirements.txt

### Generate Proto Code
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./app/proto/lob.proto

```bash

🌐 Access Points
	•	REST API: http://localhost:8000
    •	WS : ws://localhost:8000/ws


🔌 API Endpoints
Orders
    POST    /orders.                Submit a new 
    PUT     /orders/{order_id}      Modify an existing order
    DELETE  /orders/{order_id}      Cancel an order

Market Data
    WS     /ws/trades              Fetch Realtime trades
    WS     /ws/book/{ticker}       Fetch current Limit Order Book for the ticker