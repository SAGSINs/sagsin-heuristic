from typing import Any, Optional, Dict, Any as AnyType, Iterator
import datetime
import grpc

from proto import heuristic_pb2_grpc, heuristic_pb2
from proto import algorithm_stream_pb2_grpc, algorithm_stream_pb2
from ..core import GraphManager
from .heuristic_engine import HeuristicEngine
from ..analysis import StabilityAnalyzer


class HeuristicServiceServicer(heuristic_pb2_grpc.HeuristicServiceServicer, algorithm_stream_pb2_grpc.AlgorithmStreamServiceServicer):
    def __init__(self):
        self.graph_manager = GraphManager()
        self.heuristic_engine = HeuristicEngine(self.graph_manager)
        self.stability_analyzer = StabilityAnalyzer()
        
        print("[HEURISTIC] Service initialized with gRPC streaming")

    def RunAlgorithm(self, request: algorithm_stream_pb2.AlgorithmRunRequest, context: Any) -> Iterator[algorithm_stream_pb2.AlgorithmStreamEvent]:
        """
        gRPC server-side streaming for algorithm execution.
        Backend calls this method, and we stream back events.
        """
        algo = request.algo
        src = request.src
        dst = request.dst
        
        print(f"[HEURISTIC] 📥 gRPC RunAlgorithm: {algo} from {src} to {dst}")
        
        try:
            # Send run start event
            yield algorithm_stream_pb2.AlgorithmStreamEvent(
                run_start=algorithm_stream_pb2.AlgorithmRunStart(
                    algo=algo,
                    src=src,
                    dst=dst
                )
            )
            
            # Store steps to yield later (can't yield from callback)
            step_events = []
            
            # Callback to collect steps
            def on_step(ev: Dict[str, AnyType]):
                step_event = algorithm_stream_pb2.AlgorithmStep(
                    algo=ev.get('algo', algo),
                    step=ev.get('step', 0),
                    action=ev.get('action', ''),
                    node=ev.get('node', ''),
                    from_node=ev.get('from', ''),
                    to_node=ev.get('to', ''),
                    open_size=ev.get('open_size', 0),
                    g=ev.get('g', 0.0),
                    f=ev.get('f', 0.0),
                    dist=ev.get('dist', 0.0)
                )
                
                # Add path if present
                if 'path' in ev and ev['path']:
                    step_event.path.extend(ev['path'])
                
                step_events.append(algorithm_stream_pb2.AlgorithmStreamEvent(step=step_event))
            
            # Run the algorithm
            result = self.heuristic_engine.find_optimal_route(src, dst, algo, on_step=on_step)
            
            # Yield all collected step events
            for step_event in step_events:
                yield step_event
            
            # Send completion event
            complete_event = algorithm_stream_pb2.AlgorithmComplete(
                algo=algo,
                src=src,
                dst=dst
            )
            
            if result:
                route_result = algorithm_stream_pb2.RouteResult(
                    path=result.path,
                    total_weight=result.total_weight,
                    total_delay_ms=result.total_delay,
                    total_jitter_ms=result.total_jitter,
                    avg_loss_rate=result.average_loss_rate,
                    min_bandwidth_mbps=result.min_bandwidth,
                    hop_count=result.hop_count,
                    stability_score=result.stability_score
                )
                complete_event.result.CopyFrom(route_result)
            
            yield algorithm_stream_pb2.AlgorithmStreamEvent(complete=complete_event)
            print(f"[HEURISTIC] ✅ Algorithm {algo} completed")
            
        except Exception as e:
            print(f"[HEURISTIC] ❌ Error in RunAlgorithm: {e}")
            import traceback
            traceback.print_exc()
            # Optionally yield an error event or let gRPC handle it
            context.abort(grpc.StatusCode.INTERNAL, f"Algorithm execution failed: {str(e)}")
    
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