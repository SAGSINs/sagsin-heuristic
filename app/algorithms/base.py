from typing import List, Optional
from dataclasses import dataclass


@dataclass
class RouteResult:
    path: List[str]
    total_weight: float
    total_delay: float
    total_jitter: float
    average_loss_rate: float
    min_bandwidth: float
    hop_count: int
    stability_score: float


class BaseAlgorithm:
    def __init__(self, graph_manager):
        self.graph_manager = graph_manager
    
    def find_route(self, src: str, dst: str) -> Optional[RouteResult]:
        raise NotImplementedError("Subclasses must implement find_route method")
    
    def _calculate_route_metrics(self, path: List[str], graph) -> RouteResult:
        if len(path) < 2:
            return RouteResult(
                path=path,
                total_weight=0.0,
                total_delay=0.0,
                total_jitter=0.0,
                average_loss_rate=0.0,
                min_bandwidth=float('inf'),
                hop_count=0,
                stability_score=1.0
            )
        
        total_weight = 0.0
        total_delay = 0.0
        total_jitter = 0.0
        total_loss_rate = 0.0
        min_bandwidth = float('inf')
        edge_count = 0
        
        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            
            if graph.has_edge(src, dst):
                edge_data = graph[src][dst]
                
                total_weight += edge_data.get('weight', 1.0)
                total_delay += edge_data.get('delay_ms', 0.0)
                total_jitter += edge_data.get('jitter_ms', 0.0)
                total_loss_rate += edge_data.get('loss_rate', 0.0)
                
                bandwidth = edge_data.get('bandwidth_mbps', 0.0)
                if bandwidth > 0:
                    min_bandwidth = min(min_bandwidth, bandwidth)
                
                edge_count += 1
        
        average_loss_rate = total_loss_rate / edge_count if edge_count > 0 else 0.0
        
        if min_bandwidth == float('inf'):
            min_bandwidth = 0.0
        
        stability_score = max(0.0, 1.0 - (total_jitter / 1000.0) - (average_loss_rate * 10.0))
        stability_score = min(1.0, stability_score)
        
        return RouteResult(
            path=path,
            total_weight=total_weight,
            total_delay=total_delay,
            total_jitter=total_jitter,
            average_loss_rate=average_loss_rate,
            min_bandwidth=min_bandwidth,
            hop_count=len(path) - 1,
            stability_score=stability_score
        )