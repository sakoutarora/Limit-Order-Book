from src.api.grpc_server import serve
import asyncio

if __name__ == "__main__":
    asyncio.run(serve())
