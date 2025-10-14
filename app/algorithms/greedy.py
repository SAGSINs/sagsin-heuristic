from typing import Optional
from .base import BaseAlgorithm, RouteResult


class GreedyAlgorithm(BaseAlgorithm):
    def find_route(self, src: str, dst: str) -> Optional[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph:
            return None
        
        visited = set()
        current = src
        path = [src]
        
        while current != dst:
            if current in visited:
                return None
                
            visited.add(current)
            neighbors = list(graph.neighbors(current))
            
            if not neighbors:
                return None  
            
            neighbors = [n for n in neighbors if n not in visited]
            
            if not neighbors:
                return None 
            
            best_neighbor = min(
                neighbors,
                key=lambda n: self._simple_heuristic(n, dst, graph)
            )
            
            path.append(best_neighbor)
            current = best_neighbor
            
            if len(path) > len(graph.nodes()):
                return None
        
        return self._calculate_route_metrics(path, graph)
    
    def _simple_heuristic(self, u: str, v: str, graph) -> float:
        if u == v:
            return 0.0
        
        u_type = graph.nodes[u].get('type', 'unknown')
        v_type = graph.nodes[v].get('type', 'unknown')
        
        if u_type == v_type:
            return 10.0 
        
        priority = {
            'ground_station': 1,
            'satellite': 2, 
            'ship': 3,
            'drone': 4,
            'mobile_device': 5
        }
        
        u_priority = priority.get(u_type, 6)
        v_priority = priority.get(v_type, 6)
        
        return abs(u_priority - v_priority) * 20.0