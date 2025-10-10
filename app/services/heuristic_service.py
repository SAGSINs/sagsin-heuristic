from typing import Any
import datetime

from proto import heuristic_pb2_grpc, heuristic_pb2


class HeuristicServiceServicer(heuristic_pb2_grpc.HeuristicServiceServicer):
    async def UpdateGraph(self, request: heuristic_pb2.GraphSnapshot, context: Any) -> heuristic_pb2.UpdateResponse:
        # Print a concise summary to stdout
        ts = request.timestamp or datetime.datetime.utcnow().isoformat()
        print(f"Received GraphSnapshot at {ts}")
        print(f"  Nodes: {len(request.nodes)}; Links: {len(request.links)}")

        # Print nodes (id, type, status) — avoid huge dumps
        for n in request.nodes:
            m = n.metrics
            print(f"  - Node {n.id} (type={n.type} status={n.status}) metrics={{{m.cpu_load:.2f}, {m.jitter_ms:.2f}, q={m.queue_len}, t={m.throughput_mbps:.2f}}}")

        # Print links briefly
        for l in request.links:
            m = l.metrics
            print(f"  - Link {l.src} -> {l.dst} (available={l.available}) metrics={{delay={m.delay_ms:.2f}, jitter={m.jitter_ms:.2f}, bw={m.bandwidth_mbps:.2f}}}")

        return heuristic_pb2.UpdateResponse(success=True, message="Snapshot received and printed")
