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
        
        step = 0
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
                key=lambda n: (
                    0.6 * graph[current][n].get('weight', 100.0) +
                    0.4 * self._simple_heuristic(n, dst, graph)
                )
            )
            
            # Emit selection step
            self._emit_step({'algo': 'greedy', 'action': 'select', 'from': current, 'to': best_neighbor, 'step': step})
            step += 1
            path.append(best_neighbor)
            current = best_neighbor
            
            if len(path) > len(graph.nodes()):
                return None
        
        self._emit_step({
            'algo': 'greedy', 
            'action': 'complete', 
            'path': path,
            'node': dst
        })
        return self._calculate_route_metrics(path, graph)
    
    def _simple_heuristic(self, u: str, v: str, graph) -> float:
        if u == v:
            return 0.0
        
        u_type = graph.nodes[u].get('type', 'unknown')
        v_type = graph.nodes[v].get('type', 'unknown')

        if u_type == v_type:
            return 5.0
        
        priority = {
            'ground_station': 1,
            'satellite': 2, 
            'ship': 3,
            'drone': 4,
            'mobile_device': 5
        }
        
        u_priority = priority.get(u_type, 6)
        v_priority = priority.get(v_type, 6)
        
        priority_score = abs(u_priority - v_priority) * 15.0

        stability_penalty = 0.0
        if u_type in ['mobile_device', 'drone']:
            stability_penalty = 10.0
        
        return priority_score + stability_penalty