import networkx as nx
from typing import Optional
from .base import BaseAlgorithm, RouteResult


class AStarAlgorithm(BaseAlgorithm):
    def find_route(self, src: str, dst: str) -> Optional[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph:
            return None
            
        try:
            # Manual A* to emit steps
            import heapq
            open_set = []
            heapq.heappush(open_set, (0, src))
            came_from = {}
            g_score = {node: float('inf') for node in graph.nodes}
            g_score[src] = 0.0
            f_score = {node: float('inf') for node in graph.nodes}
            f_score[src] = self._network_heuristic(src, dst, graph)

            visited = set()
            step_index = 0

            while open_set:
                _, current = heapq.heappop(open_set)
                if current in visited:
                    continue
                visited.add(current)

                # Emit expansion step
                self._emit_step({
                    'algo': 'astar',
                    'step': step_index,
                    'action': 'expand',
                    'node': current,
                    'open_size': len(open_set),
                    'g': g_score.get(current, float('inf')),
                    'f': f_score.get(current, float('inf')),
                })
                step_index += 1

                if current == dst:
                    path = [current]
                    while current in came_from:
                        current = came_from[current]
                        path.append(current)
                    path.reverse()
                    self._emit_step({'algo': 'astar', 'action': 'complete', 'path': path})
                    return self._calculate_route_metrics(path, graph)

                for neighbor in graph.neighbors(current):
                    tentative_g = g_score[current] + graph[current][neighbor].get('weight', 1.0)
                    if tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self._network_heuristic(neighbor, dst, graph)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        # Emit neighbor consideration
                        self._emit_step({
                            'algo': 'astar',
                            'step': step_index,
                            'action': 'consider',
                            'from': current,
                            'to': neighbor,
                            'g': g_score[neighbor],
                            'f': f_score[neighbor],
                        })
                        step_index += 1
            
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