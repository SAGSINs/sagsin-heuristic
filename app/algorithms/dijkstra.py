import networkx as nx
from typing import Optional
from .base import BaseAlgorithm, RouteResult


class DijkstraAlgorithm(BaseAlgorithm):
    def find_route(self, src: str, dst: str) -> Optional[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph:
            return None
            
        try:
            path = nx.shortest_path(graph, src, dst, weight='weight')
            return self._calculate_route_metrics(path, graph)
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None