# Simple logging utilities

class SimpleLogger:
    def __init__(self, name: str):
        self.name = name
    
    def debug(self, message: str):
        pass  # Skip debug messages
    
    def info(self, message: str):
        print(f"[{self.name}] {message}")
    
    def warning(self, message: str):
        print(f"[{self.name}] WARNING: {message}")
    
    def error(self, message: str):
        print(f"[{self.name}] ERROR: {message}")


class PerformanceLogger:
    def __init__(self, operation: str, logger):
        self.operation = operation
        self.logger = logger
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Skip performance logging


def get_logger(name: str):
    return SimpleLogger(name)


def log_graph_update(nodes_count: int, links_count: int, update_time_ms: float):
    print(f"[HEURISTIC] Graph updated: {nodes_count} nodes, {links_count} links")


def log_route_calculation(src: str, dst: str, algorithm: str, result, calculation_time_ms: float):
    if result:
        print(f"[HEURISTIC] Route found [{algorithm}]: {src} -> {dst} ({result.hop_count} hops)")
    else:
        print(f"[HEURISTIC] No route found [{algorithm}]: {src} -> {dst}")