from typing import Any
import datetime

from proto import heuristic_pb2_grpc, heuristic_pb2
from ..core import GraphManager
from .heuristic_engine import HeuristicEngine
from ..analysis import StabilityAnalyzer


class HeuristicServiceServicer(heuristic_pb2_grpc.HeuristicServiceServicer):
    def __init__(self):
        self.graph_manager = GraphManager()
        self.heuristic_engine = HeuristicEngine(self.graph_manager)
        self.stability_analyzer = StabilityAnalyzer()
        
        print("[HEURISTIC] Service initialized")
    
    async def UpdateGraph(self, request: heuristic_pb2.GraphSnapshot, context: Any) -> heuristic_pb2.UpdateResponse:
        try:
            print(f"[HEURISTIC] UpdateGraph: {len(request.nodes)} nodes, {len(request.links)} links")

            ts = request.timestamp or datetime.datetime.utcnow().isoformat()
            timestamp = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            success = self.graph_manager.update_graph(request)
            
            if not success:
                return heuristic_pb2.UpdateResponse(
                    success=False,
                    message="Failed to update graph"
                )
            
            await self._update_stability_metrics(request, timestamp)
            
            return heuristic_pb2.UpdateResponse(
                success=True,
                message=f"Graph updated successfully with {len(request.nodes)} nodes and {len(request.links)} links"
            )
            
        except Exception as e:
            print(f"[HEURISTIC] ERROR: {e}")
            return heuristic_pb2.UpdateResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def RequestRoute(self, request, context):
        try:
            src = request.source_node_id
            dst = request.destination_node_id
            algorithm = getattr(request, 'algorithm', 'astar')
            
            print(f"[HEURISTIC] RouteRequest: {src} -> {dst} using {algorithm}")
            
            route_result = self.heuristic_engine.find_optimal_route(src, dst, algorithm)
            
            if route_result:
                return heuristic_pb2.RouteResponse(
                    success=True,
                    path=route_result.path,
                    total_weight=route_result.total_weight,
                    total_delay_ms=route_result.total_delay,
                    stability_score=route_result.stability_score,
                    hop_count=route_result.hop_count
                )
            else:
                return heuristic_pb2.RouteResponse(
                    success=False,
                    message=f"No route found from {src} to {dst}"
                )
                
        except Exception as e:
            print(f"[HEURISTIC] Route ERROR: {e}")
            return heuristic_pb2.RouteResponse(
                success=False,
                message=f"Route calculation error: {str(e)}"
            )
    
    async def _update_stability_metrics(self, snapshot: heuristic_pb2.GraphSnapshot, timestamp: datetime.datetime):
        for node in snapshot.nodes:
            node_metrics = {
                'cpu_load': node.metrics.cpu_load,
                'jitter_ms': node.metrics.jitter_ms,
                'queue_len': float(node.metrics.queue_len),
                'throughput_mbps': node.metrics.throughput_mbps
            }
            self.stability_analyzer.update_node_metrics(node.id, timestamp, node_metrics)
        
        for link in snapshot.links:
            link_id = f"{link.src}_{link.dst}"
            link_metrics = {
                'delay_ms': link.metrics.delay_ms,
                'jitter_ms': link.metrics.jitter_ms,
                'loss_rate': link.metrics.loss_rate,
                'bandwidth_mbps': link.metrics.bandwidth_mbps
            }
            self.stability_analyzer.update_link_metrics(link_id, timestamp, link_metrics)