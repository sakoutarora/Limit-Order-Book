🚀 High-Performance Trading System

This project implements a complete, high-performance trading system built on a decoupled, microservice-oriented architecture. It consists of two primary components:

engine: A core Matching Engine built with gRPC for high-speed, O(1) order book operations and persistent state management.

api: A user-facing Trading Gateway built with FastAPI, providing a REST API for order management and WebSockets for real-time data streaming.

🧭 System Architecture

The system is designed for high throughput and low latency. All client interactions are handled by the api gateway, which then communicates with the core engine via gRPC for all mission-critical order matching logic.

A simple flow diagram of the architecture:
```bash

[ Trading Client (UI/Bot) ]
        |
        | (REST for Orders)
        | (WebSocket for Data)
        |
+-------v-------+
|               |
|   api         |  (FastAPI Trading Gateway)
|               |
+-------|-------+
        |
        | (gRPC)
        |
+-------v-------+
|               |
|   engine      |  (Core Matching Engine)
|               |
+-------|-------+
        |
        | (Persistence)
        |
[ WAL & Snapshots ]
```

📁 Project Structure

.
├── api/          # REST/WebSocket Gateway (FastAPI)
├── engine/       # Core Matching Engine (gRPC)
└── README.md     # This overview


🧩 Core Components

1. Matching Engine (engine/)

This is the heart of the trading system. It is a high-performance gRPC service responsible for maintaining the Limit Order Book (LOB).

Technology: Python, gRPC

Core Logic: Maintains bids/asks in sorted dictionaries, aiming for amortized O(1) complexity for core operations.

Persistence: Guarantees data integrity through a Write-Ahead Log (WAL) and periodic snapshotting of the LOB state.

For more details, see the engine/README.md.

2. Trading Gateway (api/)

This is the public-facing service that clients interact with. It translates user-friendly REST and WebSocket communications into high-performance gRPC calls to the matching engine.

Technology: Python, FastAPI

REST API: Provides endpoints for submitting, modifying, and canceling orders.

WebSocket API: Streams real-time trade executions and Limit Order Book (LOB) updates to connected clients.

Integration: Communicates with the engine via gRPC and uses Redis for caching/task management.

For more details, see the api/README.md.

⚙️ Getting Started

To run the complete system, you must start both services.

Prerequisites

Python 3.8+

Docker (Recommended)

protoc compiler (for gRPC code generation)

1. Run the Matching Engine

First, set up and run the engine service, which acts as the gRPC server.

cd engine
# (Follow setup instructions in engine/README.md)
# ... install dependencies, generate proto code ...
python -m src.api.grpc_server


2. Run the API Gateway

Once the engine is running, set up and run the api service in a separate terminal.

cd api
# (Follow setup instructions in api/README.md)
# ... install dependencies, generate proto code ...
uvicorn app.main:app --host 0.0.0.0 --port 8000


3. Accessing the System

REST API: http://localhost:8000

WebSocket: ws://localhost:8000/ws