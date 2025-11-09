import networkx as nx
import numpy as np
import threading
from typing import Dict, List, Optional
from datetime import datetime

from .data_structures import NodeData, LinkData

DOWN_NODE_PENALTY = 1e9    
DOWN_LINK_PENALTY = 5e8   
MIN_WEIGHT_FLOOR = 0.0001  

class GraphOperations:
    def __init__(self):
        self.graph: nx.Graph = nx.Graph()
        self.nodes_data: Dict[str, NodeData] = {}
        self.links_data: Dict[str, LinkData] = {}
        self._lock = threading.RLock()
        self.last_update: Optional[datetime] = None
    
    def clear_graph(self):
        with self._lock:
            self.graph.clear()
            self.nodes_data.clear()
            self.links_data.clear()
    
    def add_node_from_proto(self, node_pb, timestamp: datetime):
        with self._lock:
            node_data = NodeData(
                id=node_pb.id,
                type=node_pb.type,
                status=node_pb.status,
                cpu_load=node_pb.metrics.cpu_load,
                jitter_ms=node_pb.metrics.jitter_ms,
                queue_len=node_pb.metrics.queue_len,
                throughput_mbps=node_pb.metrics.throughput_mbps,
                last_updated=timestamp
            )
            
            self.nodes_data[node_pb.id] = node_data
            self.graph.add_node(
                node_pb.id,
                type=node_pb.type,
                status=node_pb.status,
                cpu_load=node_pb.metrics.cpu_load,
                jitter_ms=node_pb.metrics.jitter_ms,
                queue_len=node_pb.metrics.queue_len,
                throughput_mbps=node_pb.metrics.throughput_mbps
            )
    
    def add_link_from_proto(self, link_pb, timestamp: datetime):
        with self._lock:
            link_id = f"{link_pb.src}_{link_pb.dst}"
            link_data = LinkData(
                src=link_pb.src,
                dst=link_pb.dst,
                available=link_pb.available,
                delay_ms=link_pb.metrics.delay_ms,
                jitter_ms=link_pb.metrics.jitter_ms,
                loss_rate=link_pb.metrics.loss_rate,
                bandwidth_mbps=link_pb.metrics.bandwidth_mbps,
                last_updated=timestamp
            )
            self.links_data[link_id] = link_data

            bandwidth_mbps = link_pb.metrics.bandwidth_mbps or 0.0
            bandwidth_penalty = 1000.0 / (bandwidth_mbps + 1.0)

            node_penalty = 0.0
            src_node = self.nodes_data.get(link_pb.src)
            dst_node = self.nodes_data.get(link_pb.dst)

            if src_node:
                node_penalty += src_node.cpu_load * 5.0 + src_node.queue_len * 0.5
            if dst_node:
                node_penalty += dst_node.cpu_load * 5.0 + dst_node.queue_len * 0.5

            base_weight = (
                (link_pb.metrics.delay_ms or 0.0) +
                (link_pb.metrics.jitter_ms or 0.0) * 2.0 +
                (link_pb.metrics.loss_rate or 0.0) * 1000.0 +
                bandwidth_penalty * 0.1 +
                node_penalty
            )

            # Apply penalties for DOWN elements
            penalized = False
            if not link_pb.available:
                base_weight = max(base_weight, DOWN_LINK_PENALTY)
                penalized = True
            if (src_node and src_node.status != 'UP') or (dst_node and dst_node.status != 'UP'):
                base_weight = max(base_weight, DOWN_NODE_PENALTY)
                penalized = True

            final_weight = max(base_weight, MIN_WEIGHT_FLOOR)

            self.graph.add_edge(
                link_pb.src,
                link_pb.dst,
                weight=final_weight,
                delay_ms=link_pb.metrics.delay_ms,
                jitter_ms=link_pb.metrics.jitter_ms,
                loss_rate=link_pb.metrics.loss_rate,
                bandwidth_mbps=link_pb.metrics.bandwidth_mbps,
                available=link_pb.available,
                penalized=penalized
            )
    
    def get_neighbors(self, node_id: str) -> List[str]:
        with self._lock:
            if node_id not in self.graph:
                return []
            return list(self.graph.neighbors(node_id))
    
    def get_edge_weight(self, src: str, dst: str) -> float:
        with self._lock:
            if self.graph.has_edge(src, dst):
                return self.graph[src][dst].get('weight', np.inf)
            return np.inf
    
    def get_graph_copy(self) -> nx.Graph:
        with self._lock:
            return self.graph.copy()
    
    def is_connected(self, src: str, dst: str) -> bool:
        with self._lock:
            try:
                return nx.has_path(self.graph, src, dst)
            except nx.NodeNotFound:
                return False
    
    def get_node_count(self) -> int:
        with self._lock:
            return len(self.graph.nodes())
    
    def get_edge_count(self) -> int:
        with self._lock:
            return len(self.graph.edges())