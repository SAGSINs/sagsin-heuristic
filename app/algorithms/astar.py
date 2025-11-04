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
                    temp_node = current
                    while temp_node in came_from:
                        temp_node = came_from[temp_node]
                        path.append(temp_node)
                    path.reverse()
                    
                    self._emit_step({
                        'algo': 'astar', 
                        'action': 'complete', 
                        'path': path,
                        'node': dst,
                        'g': g_score.get(dst, 0.0),
                        'f': f_score.get(dst, 0.0)
                    })
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
        if u == v:
            return 0.0
        
        neighbors = list(graph.neighbors(u))
        if not neighbors:
            return 0.0  
        
        min_outgoing_weight = min(
            graph[u][n].get('weight', 100.0) 
            for n in neighbors
        )

        try:
            min_hops = nx.shortest_path_length(graph, u, v)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            u_type = graph.nodes[u].get('type', 'unknown')
            v_type = graph.nodes[v].get('type', 'unknown')

            if u_type == v_type:
                min_hops = 1
            elif u_type == 'ground_station' or v_type == 'ground_station':
                min_hops = 2
            else:
                min_hops = 3

        heuristic_value = float(min_outgoing_weight * max(1, min_hops))
        
        return heuristic_value