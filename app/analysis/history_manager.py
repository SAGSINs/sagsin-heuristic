import threading
from typing import Dict
from datetime import datetime
from collections import defaultdict, deque

from .metrics import MetricSnapshot


class MetricsHistoryManager:
    def __init__(self, history_window: int = 50, smoothing_factor: float = 0.3):
        self.history_window = history_window
        self.smoothing_factor = smoothing_factor
        
        self.node_metrics_history: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=history_window))
        )
        
        self.link_metrics_history: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=history_window))
        )
        
        self.node_ema: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.link_ema: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        self._lock = threading.RLock()
    
    def add_node_metric(self, node_id: str, metric_name: str, value: float, timestamp: datetime):
        with self._lock:
            snapshot = MetricSnapshot(timestamp, value)
            self.node_metrics_history[node_id][metric_name].append(snapshot)
            
            if metric_name not in self.node_ema[node_id]:
                self.node_ema[node_id][metric_name] = value
            else:
                self.node_ema[node_id][metric_name] = (
                    self.smoothing_factor * value +
                    (1 - self.smoothing_factor) * self.node_ema[node_id][metric_name]
                )
    
    def add_link_metric(self, link_id: str, metric_name: str, value: float, timestamp: datetime):
        with self._lock:
            snapshot = MetricSnapshot(timestamp, value)
            self.link_metrics_history[link_id][metric_name].append(snapshot)
            
            if metric_name not in self.link_ema[link_id]:
                self.link_ema[link_id][metric_name] = value
            else:
                self.link_ema[link_id][metric_name] = (
                    self.smoothing_factor * value +
                    (1 - self.smoothing_factor) * self.link_ema[link_id][metric_name]
                )
    
    def get_node_history(self, node_id: str, metric_name: str) -> deque:
        with self._lock:
            return self.node_metrics_history.get(node_id, {}).get(metric_name, deque())
    
    def get_link_history(self, link_id: str, metric_name: str) -> deque:
        with self._lock:
            return self.link_metrics_history.get(link_id, {}).get(metric_name, deque())
    
    def get_node_ema(self, node_id: str, metric_name: str) -> float:
        with self._lock:
            return self.node_ema.get(node_id, {}).get(metric_name, 0.0)
    
    def has_node_metric(self, node_id: str, metric_name: str) -> bool:
        with self._lock:
            return (node_id in self.node_metrics_history and 
                    metric_name in self.node_metrics_history[node_id] and
                    len(self.node_metrics_history[node_id][metric_name]) >= 2)
    
    def has_link_metric(self, link_id: str, metric_name: str) -> bool:
        with self._lock:
            return (link_id in self.link_metrics_history and 
                    metric_name in self.link_metrics_history[link_id] and
                    len(self.link_metrics_history[link_id][metric_name]) >= 2)
    
    def get_all_node_ids(self) -> list:
        with self._lock:
            return list(self.node_metrics_history.keys())
    
    def get_all_link_ids(self) -> list:
        with self._lock:
            return list(self.link_metrics_history.keys())
    
    def get_node_metric_names(self, node_id: str) -> list:
        with self._lock:
            return list(self.node_metrics_history.get(node_id, {}).keys())
    
    def get_link_metric_names(self, link_id: str) -> list:
        with self._lock:
            return list(self.link_metrics_history.get(link_id, {}).keys())