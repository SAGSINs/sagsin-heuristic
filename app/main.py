import asyncio
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import grpc
from proto import heuristic_pb2_grpc
from app.services.heuristic_service import HeuristicServiceServicer


async def serve() -> None:
    server = grpc.aio.server()
    heuristic_pb2_grpc.add_HeuristicServiceServicer_to_server(
        HeuristicServiceServicer(), server
    )

    listen_addr = os.environ.get("HEURISTIC_LISTEN", "0.0.0.0:50052")
    server.add_insecure_port(listen_addr)
    print(f"Starting Heuristic gRPC server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Shutting down server")
