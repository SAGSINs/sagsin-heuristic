import networkx as nx
import threading
from typing import Dict, Optional, List
from datetime import datetime


class GraphStats:
    def __init__(self, graph_operations):
        self.graph_ops = graph_operations
    
    def get_graph_stats(self) -> Dict:
        with self.graph_ops._lock:
            if not self.graph_ops.graph.nodes():
                return {"nodes": 0, "edges": 0, "connected": False}
                
            return {
                "nodes": len(self.graph_ops.graph.nodes()),
                "edges": len(self.graph_ops.graph.edges()),
                "connected": nx.is_connected(self.graph_ops.graph),
                "average_degree": self._calculate_average_degree(),
                "last_update": self.graph_ops.last_update.isoformat() if self.graph_ops.last_update else None,
                "density": nx.density(self.graph_ops.graph),
                "diameter": self._safe_diameter(),
                "clustering_coefficient": self._safe_clustering()
            }
    
    def _calculate_average_degree(self) -> float:
        if not self.graph_ops.graph.nodes():
            return 0.0
        return sum(dict(self.graph_ops.graph.degree()).values()) / len(self.graph_ops.graph.nodes())
    
    def _safe_diameter(self) -> Optional[int]:
        try:
            if nx.is_connected(self.graph_ops.graph):
                return nx.diameter(self.graph_ops.graph)
            return None
        except:
            return None
    
    def _safe_clustering(self) -> float:
        try:
            return nx.average_clustering(self.graph_ops.graph)
        except:
            return 0.0
    
    def get_node_centralities(self) -> Dict[str, Dict[str, float]]:
        with self.graph_ops._lock:
            if not self.graph_ops.graph.nodes():
                return {}
            
            try:
                centralities = {}
                
                degree_cent = nx.degree_centrality(self.graph_ops.graph)
                
                betweenness_cent = nx.betweenness_centrality(self.graph_ops.graph)
                
                if nx.is_connected(self.graph_ops.graph):
                    closeness_cent = nx.closeness_centrality(self.graph_ops.graph)
                else:
                    closeness_cent = {node: 0.0 for node in self.graph_ops.graph.nodes()}
                
                for node in self.graph_ops.graph.nodes():
                    centralities[node] = {
                        'degree': degree_cent.get(node, 0.0),
                        'betweenness': betweenness_cent.get(node, 0.0),
                        'closeness': closeness_cent.get(node, 0.0)
                    }
                
                return centralities
                
            except Exception as e:
                pass 
                return {}
    
    def get_critical_nodes(self, top_n: int = 5) -> List[str]:
        centralities = self.get_node_centralities()
        
        if not centralities:
            return []
        
        node_scores = {}
        for node, cents in centralities.items():
            score = (
                cents['degree'] * 0.4 +
                cents['betweenness'] * 0.4 +
                cents['closeness'] * 0.2
            )
            node_scores[node] = score
        
        sorted_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)
        return [node for node, score in sorted_nodes[:top_n]]