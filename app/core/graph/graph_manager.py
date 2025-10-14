from datetime import datetime
from proto import heuristic_pb2

from .graph_operations import GraphOperations
from .adjacency_manager import AdjacencyManager
from .graph_stats import GraphStats


class GraphManager:
    def __init__(self):
        self.graph_ops = GraphOperations()
        self.adjacency_mgr = AdjacencyManager()
        self.stats = GraphStats(self.graph_ops)
    
    def update_graph(self, snapshot: heuristic_pb2.GraphSnapshot) -> bool:
        try:
            timestamp = datetime.fromisoformat(snapshot.timestamp.replace('Z', '+00:00'))
            
            self.graph_ops.clear_graph()
            self.adjacency_mgr.clear()
            
            for node_pb in snapshot.nodes:
                self.graph_ops.add_node_from_proto(node_pb, timestamp)
            
            for link_pb in snapshot.links:
                self.graph_ops.add_link_from_proto(link_pb, timestamp)
            
            self.adjacency_mgr.build_adjacency_matrix(self.graph_ops.graph)
            self.graph_ops.last_update = timestamp
            
            return True
            
        except Exception as e:
            return False
    
    def get_neighbors(self, node_id: str):
        return self.graph_ops.get_neighbors(node_id)
    
    def get_edge_weight(self, src: str, dst: str):
        return self.graph_ops.get_edge_weight(src, dst)
    
    def get_node_count(self):
        return self.graph_ops.get_node_count()
    
    def get_edge_count(self):
        return self.graph_ops.get_edge_count()
    
    def get_graph_copy(self):
        return self.graph_ops.get_graph_copy()
    
    def is_connected(self, src: str, dst: str):
        return self.graph_ops.is_connected(src, dst)
    
    def get_adjacency_matrix(self):
        return self.adjacency_mgr.get_adjacency_matrix()
    
    def get_node_index(self, node_id: str):
        return self.adjacency_mgr.get_node_index(node_id)
    
    def get_node_by_index(self, index: int):
        return self.adjacency_mgr.get_node_by_index(index)
    
    def get_graph_stats(self):
        return self.stats.get_graph_stats()
    
    def get_node_centralities(self):
        return self.stats.get_node_centralities()
    
    def get_critical_nodes(self, top_n: int = 5):
        return self.stats.get_critical_nodes(top_n)