import networkx as nx
from typing import Optional
from .base import BaseAlgorithm, RouteResult


class DijkstraAlgorithm(BaseAlgorithm):
    def find_route(self, src: str, dst: str) -> Optional[RouteResult]:
        graph = self.graph_manager.get_graph_copy()
        
        if src not in graph or dst not in graph:
            return None
            
        try:
            # Manual Dijkstra to emit steps
            import heapq
            dist = {node: float('inf') for node in graph.nodes}
            prev = {}
            dist[src] = 0.0
            pq = [(0.0, src)]
            visited = set()
            step = 0

            while pq:
                d, u = heapq.heappop(pq)
                if u in visited:
                    continue
                visited.add(u)
                self._emit_step({'algo': 'dijkstra', 'action': 'expand', 'step': step, 'node': u, 'dist': d})
                step += 1
                if u == dst:
                    break
                for v in graph.neighbors(u):
                    w = graph[u][v].get('weight', 1.0)
                    nd = d + w
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = u
                        heapq.heappush(pq, (nd, v))
                        self._emit_step({'algo': 'dijkstra', 'action': 'relax', 'from': u, 'to': v, 'step': step, 'dist': nd})
                        step += 1

            if dst not in prev and src != dst:
                return None
            path = [dst]
            cur = dst
            while cur in prev:
                cur = prev[cur]
                path.append(cur)
            path.reverse()
            
            self._emit_step({
                'algo': 'dijkstra', 
                'action': 'complete', 
                'path': path,
                'node': dst,
                'dist': dist.get(dst, 0.0)
            })
            return self._calculate_route_metrics(path, graph)
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None