🧩 Order Engine gRPC Service

This project is an Order Engine gRPC Service that receives gRPC calls from clients to handle order-related operations.
It maintains a Limit Order Book (LOB) using two sorted dictionaries — one for asks and one for bids.
Each price level in the LOB is represented by a PriceLevel object containing an ordered dictionary of orders, inserted in the order of their order_id.

The system is designed to keep all core operations with amortized O(1) time complexity.

📁 Project Structure

```bash
engine/
├── README.md
├── src/
│   ├── models/
│   │   ├── limit_order_book.py
│   │   ├── order.py
│   │   └── price_level.py
│   ├── proto/
│   │   └── lob.proto
│   ├── service/
│   │   └── matching_engine.py
│   ├── api/
│   │   └── grpc_server.py
│   ├── controller/
│   │   └── order_grpc_controller.py
│   ├── db/
│   │   └── lob_db.py
│   ├── repository/
│   │   └── lob_repo.py
│   └── persistence/
│       ├── wal.py
│       └── snapshot.py
├── setup.py
└── requirements.txt
```bash

⚙️ Models

🏛️ LimitOrderBook

The LimitOrderBook class represents the entire LOB.

Structure:
	•	Two sorted dictionaries:
	•	bids: Sorted in descending order of price.
	•	asks: Sorted in ascending order of price.
	•	Each price level is represented by a PriceLevel object.
	•	order_map: Maps order_id → Order instance.


💰 PriceLevel

The PriceLevel class represents a price level within the LOB.

Structure:
	•	orders: An ordered dictionary mapping order_id → Order.
	•	total_qty: Tracks the total quantity of all orders at that price level.

⸻

🧬 Protobuf Compilation Command
```bash
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. ./src/proto/lob.proto
```bash