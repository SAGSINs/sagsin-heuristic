from typing import List, Optional, Callable, Dict, Any
from ..core import GraphManager
from ..algorithms import RouteResult, AStarAlgorithm, DijkstraAlgorithm, GreedyAlgorithm
import networkx as nx


class HeuristicEngine:
    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager
        
        self.astar = AStarAlgorithm(graph_manager)
        self.dijkstra = DijkstraAlgorithm(graph_manager)
        self.greedy = GreedyAlgorithm(graph_manager)
    
    def find_optimal_route(self, src: str, dst: str, algorithm: str = "astar", on_step: Optional[Callable[[Dict[str, Any]], None]] = None) -> Optional[RouteResult]:
        algorithm_map = {
            "astar": self.astar,
            "dijkstra": self.dijkstra,
            "greedy": self.greedy
        }
        
        if algorithm not in algorithm_map:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # If algorithm supports step callbacks, bind it
        alg = algorithm_map[algorithm]
        if hasattr(alg, 'set_step_callback') and callable(getattr(alg, 'set_step_callback')):
            alg.set_step_callback(on_step)
        return alg.find_route(src, dst)
    
    def find_k_shortest_paths(self, src: str, dst: str, k: int = 3) -> List[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph:
            return []
        
        try:
            paths = list(nx.shortest_simple_paths(graph, src, dst, weight='weight'))
            
            results = []
            for path in paths[:k]: 
                result = self.dijkstra._calculate_route_metrics(path, graph)
                results.append(result)
            
            return results
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def find_backup_routes(self, src: str, dst: str, primary_path: List[str]) -> List[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph or len(primary_path) < 2:
            return []
        
        edges_to_remove = []
        for i in range(len(primary_path) - 1):
            u, v = primary_path[i], primary_path[i + 1]
            if graph.has_edge(u, v):
                edges_to_remove.append((u, v))
        
        backup_graph = graph.copy()
        backup_graph.remove_edges_from(edges_to_remove)
        
        try:
            backup_path = nx.shortest_path(backup_graph, src, dst, weight='weight')
            backup_result = self.dijkstra._calculate_route_metrics(backup_path, graph)
            return [backup_result]
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []