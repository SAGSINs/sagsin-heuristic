from typing import Dict, List, Optional
from datetime import datetime

from .history_manager import MetricsHistoryManager
from .stability_calculator import StabilityCalculator
from .metrics import StabilityMetrics, MetricSnapshot


class StabilityAnalyzer:
    def __init__(self, history_window: int = 50, smoothing_factor: float = 0.3):
        self.history_manager = MetricsHistoryManager(history_window, smoothing_factor)
        self.calculator = StabilityCalculator()
    
    def update_node_metrics(self, node_id: str, timestamp: datetime, metrics: Dict[str, float]):
        for metric_name, value in metrics.items():
            self.history_manager.add_node_metric(node_id, metric_name, value, timestamp)
    
    def update_link_metrics(self, link_id: str, timestamp: datetime, metrics: Dict[str, float]):
        for metric_name, value in metrics.items():
            self.history_manager.add_link_metric(link_id, metric_name, value, timestamp)
    
    def calculate_node_stability(self, node_id: str, metric_name: str) -> Optional[StabilityMetrics]:
        if not self.history_manager.has_node_metric(node_id, metric_name):
            return None
        
        history = self.history_manager.get_node_history(node_id, metric_name)
        return self.calculator.calculate_stability_metrics(history)
    
    def calculate_link_stability(self, link_id: str, metric_name: str) -> Optional[StabilityMetrics]:
        if not self.history_manager.has_link_metric(link_id, metric_name):
            return None
        
        history = self.history_manager.get_link_history(link_id, metric_name)
        return self.calculator.calculate_stability_metrics(history)
    
    def get_overall_node_stability(self, node_id: str) -> Optional[float]:
        stability_scores = []
        
        for metric_name in self.history_manager.get_node_metric_names(node_id):
            stability = self.calculate_node_stability(node_id, metric_name)
            if stability:
                stability_scores.append(stability.stability_score)
        
        if not stability_scores:
            return None
        
        return self.calculator.calculate_weighted_stability(stability_scores, 'node')
    
    def get_overall_link_stability(self, link_id: str) -> Optional[float]:
        stability_scores = []
        
        for metric_name in self.history_manager.get_link_metric_names(link_id):
            stability = self.calculate_link_stability(link_id, metric_name)
            if stability:
                stability_scores.append(stability.stability_score)
        
        if not stability_scores:
            return None
        
        return self.calculator.calculate_weighted_stability(stability_scores, 'link')
    
    def get_network_stability(self) -> Dict[str, float]:
        node_stabilities = []
        link_stabilities = []
        
        for node_id in self.history_manager.get_all_node_ids():
            stability = self.get_overall_node_stability(node_id)
            if stability is not None:
                node_stabilities.append(stability)
        
        for link_id in self.history_manager.get_all_link_ids():
            stability = self.get_overall_link_stability(link_id)
            if stability is not None:
                link_stabilities.append(stability)
        
        return self.calculator.calculate_network_stability(node_stabilities, link_stabilities)
    
    def predict_next_value(self, node_id: str, metric_name: str) -> Optional[float]:
        return self.history_manager.get_node_ema(node_id, metric_name)
    
    def detect_anomalies(self, node_id: str, metric_name: str, threshold: float = 3.0) -> List[MetricSnapshot]:
        stability = self.calculate_node_stability(node_id, metric_name)
        if not stability:
            return []
        
        history = self.history_manager.get_node_history(node_id, metric_name)
        return self.calculator.detect_anomalies(history, stability, threshold)