from typing import Any, Optional, Dict, Any as AnyType
import datetime

from proto import heuristic_pb2_grpc, heuristic_pb2
from ..core import GraphManager
from .heuristic_engine import HeuristicEngine
from ..analysis import StabilityAnalyzer
import os
import socketio


class HeuristicServiceServicer(heuristic_pb2_grpc.HeuristicServiceServicer):
    def __init__(self):
        self.graph_manager = GraphManager()
        self.heuristic_engine = HeuristicEngine(self.graph_manager)
        self.stability_analyzer = StabilityAnalyzer()
        self.sio: Optional[Any] = None
        
        print("[HEURISTIC] Service initialized")
        self._init_socket()

    def _init_socket(self):
        if socketio is None:
            print("[HEURISTIC] socketio not available; step streaming disabled")
            return
        try:
            backend_url = os.environ.get('BACKEND_SOCKET_URL', 'http://localhost:3000')
            self.sio = socketio.Client()

            @self.sio.on('heuristic:request-run')
            def on_request_run(data):
                try:
                    src = data.get('src')
                    dst = data.get('dst')
                    algo = data.get('algo', 'astar')
                    print(f"[HEURISTIC] 🚀 Running {algo}: {src} → {dst}")
                    def on_step(ev: Dict[str, AnyType]):
                        if self.sio:
                            self.sio.emit('heuristic:step', ev)
                    if self.sio:
                        self.sio.emit('heuristic:run-start', {'algo': algo, 'src': src, 'dst': dst})
                    result = self.heuristic_engine.find_optimal_route(src, dst, algo, on_step=on_step)
                    if self.sio:
                        payload = {'algo': algo, 'src': src, 'dst': dst, 'result': None}
                        if result:
                            payload['result'] = {
                                'path': result.path,
                                'total_weight': result.total_weight,
                                'total_delay_ms': result.total_delay,
                                'total_jitter_ms': result.total_jitter,
                                'avg_loss_rate': result.average_loss_rate,
                                'min_bandwidth_mbps': result.min_bandwidth,
                                'hop_count': result.hop_count,
                                'stability_score': result.stability_score,
                            }
                        self.sio.emit('heuristic:complete', payload)
                        print(f"[HEURISTIC] ✅ Emitted heuristic:complete")
                except Exception as e:
                    print(f"[HEURISTIC] ❌ Error in request-run: {e}")
                    import traceback
                    traceback.print_exc()

            self.sio.connect(backend_url, transports=['websocket'])
            print(f"[HEURISTIC] ✅ Socket connected: {self.sio.connected}")
        except Exception as e:
            print(f"[HEURISTIC] 🚨 Socket init failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def UpdateGraph(self, request: heuristic_pb2.GraphSnapshot, context: Any) -> heuristic_pb2.UpdateResponse:
        try:
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