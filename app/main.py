import asyncio
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import grpc
from proto import heuristic_pb2_grpc, algorithm_stream_pb2_grpc
from app.services.heuristic_service import HeuristicServiceServicer


async def serve() -> None:
    server = grpc.aio.server()
    servicer = HeuristicServiceServicer()
    
    # Register both services
    heuristic_pb2_grpc.add_HeuristicServiceServicer_to_server(servicer, server)
    algorithm_stream_pb2_grpc.add_AlgorithmStreamServiceServicer_to_server(servicer, server)

    listen_addr = os.environ.get("HEURISTIC_LISTEN", "0.0.0.0:50052")
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Shutting down server")
