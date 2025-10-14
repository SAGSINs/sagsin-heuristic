import networkx as nx
from typing import Optional
from .base import BaseAlgorithm, RouteResult


class AStarAlgorithm(BaseAlgorithm):
    def find_route(self, src: str, dst: str) -> Optional[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph:
            return None
            
        try:
            path = nx.astar_path(
                graph, 
                src, 
                dst, 
                heuristic=lambda u, v: self._network_heuristic(u, v, graph),
                weight='weight'
            )
            
            return self._calculate_route_metrics(path, graph)
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def _network_heuristic(self, u: str, v: str, graph: nx.Graph) -> float:
        """Network-aware heuristic for A* algorithm"""
        if u == v:
            return 0.0
        
        u_type = graph.nodes[u].get('type', 'unknown')
        v_type = graph.nodes[v].get('type', 'unknown')
        
        type_delays = {
            ('satellite', 'satellite'): 20, 
            ('satellite', 'ground_station'): 250, 
            ('satellite', 'ship'): 260,     
            ('satellite', 'mobile_device'): 270,
            ('satellite', 'drone'): 240, 
            
            ('ground_station', 'ground_station'): 10,
            ('ground_station', 'mobile_device'): 15, 
            ('ground_station', 'ship'): 30,        
            ('ground_station', 'drone'): 25,        
            
            ('ship', 'ship'): 50,             
            ('ship', 'mobile_device'): 40,    
            ('ship', 'drone'): 35,           
            
            ('mobile_device', 'mobile_device'): 20,
            ('mobile_device', 'drone'): 30,    
            
            ('drone', 'drone'): 25,        
        }
        
        delay_key = (u_type, v_type) if (u_type, v_type) in type_delays else (v_type, u_type)
        base_delay = type_delays.get(delay_key, 100)  
        
        return float(base_delay + abs(hash(u + v)) % 10)