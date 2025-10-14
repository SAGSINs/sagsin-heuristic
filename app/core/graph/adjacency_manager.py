import numpy as np
import threading
from typing import Dict, Optional


class AdjacencyManager:
    def __init__(self):
        self.adjacency_matrix: Optional[np.ndarray] = None
        self.node_index_map: Dict[str, int] = {}
        self.index_node_map: Dict[int, str] = {}
        self._lock = threading.RLock()
    
    def build_adjacency_matrix(self, graph):
        with self._lock:
            if not graph.nodes():
                self.adjacency_matrix = None
                self.node_index_map.clear()
                self.index_node_map.clear()
                return
                
            nodes = list(graph.nodes())
            n = len(nodes)
            
            self.node_index_map = {node: i for i, node in enumerate(nodes)}
            self.index_node_map = {i: node for i, node in enumerate(nodes)}
            
            self.adjacency_matrix = np.full((n, n), np.inf, dtype=np.float64)
            
            np.fill_diagonal(self.adjacency_matrix, 0)
            
            for src, dst, data in graph.edges(data=True):
                i = self.node_index_map[src]
                j = self.node_index_map[dst]
                weight = data.get('weight', 1.0)
                
                self.adjacency_matrix[i][j] = weight
                self.adjacency_matrix[j][i] = weight
    
    def get_adjacency_matrix(self) -> Optional[np.ndarray]:
        with self._lock:
            if self.adjacency_matrix is not None:
                return self.adjacency_matrix.copy()
            return None
    
    def get_node_index(self, node_id: str) -> Optional[int]:
        with self._lock:
            return self.node_index_map.get(node_id)
    
    def get_node_by_index(self, index: int) -> Optional[str]:
        with self._lock:
            return self.index_node_map.get(index)
    
    def clear(self):
        with self._lock:
            self.adjacency_matrix = None
            self.node_index_map.clear()
            self.index_node_map.clear()