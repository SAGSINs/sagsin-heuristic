import numpy as np
from typing import Optional, List
from collections import deque

from .metrics import StabilityMetrics, MetricsCalculator, MetricSnapshot


class StabilityCalculator:
    @staticmethod
    def calculate_stability_metrics(history: deque) -> StabilityMetrics:
        values = [snapshot.value for snapshot in history]
        
        mean = np.mean(values)
        variance = np.var(values, ddof=1) if len(values) > 1 else 0.0
        std_deviation = np.sqrt(variance)
        
        cv = std_deviation / mean if mean != 0 else float('inf')
        
        if len(values) >= 3:
            x = np.arange(len(values))
            trend = np.polyfit(x, values, 1)[0]  
        else:
            trend = 0.0
        
        stability_score = MetricsCalculator.calculate_stability_score(cv, abs(trend), mean)
        
        return StabilityMetrics(
            mean=mean,
            variance=variance,
            std_deviation=std_deviation,
            coefficient_of_variation=cv,
            trend=trend,
            stability_score=stability_score
        )
    
    @staticmethod
    def calculate_weighted_stability(stability_scores: List[float], entity_type: str = 'node') -> float:
        if not stability_scores:
            return 0.0
        
        if entity_type == 'node':
            metric_weights = {
                'cpu_load': 0.3,
                'jitter_ms': 0.3,
                'queue_len': 0.2,
                'throughput_mbps': 0.2
            }
        else: 
            metric_weights = {
                'delay_ms': 0.35,
                'jitter_ms': 0.35,
                'loss_rate': 0.2,
                'bandwidth_mbps': 0.1
            }
        
        if len(stability_scores) == len(metric_weights):
            weighted_sum = sum(
                score * weight for score, weight in 
                zip(stability_scores, metric_weights.values())
            )
            return weighted_sum
        else:
            return np.mean(stability_scores)
    
    @staticmethod
    def detect_anomalies(history: deque, stability: StabilityMetrics, threshold: float = 3.0) -> List[MetricSnapshot]:
        if not stability:
            return []
        
        anomalies = []
        for snapshot in history:
            z_score = abs(snapshot.value - stability.mean) / (stability.std_deviation + 0.001)
            if z_score > threshold:
                anomalies.append(snapshot)
        
        return anomalies
    
    @staticmethod
    def calculate_network_stability(node_stabilities: List[float], link_stabilities: List[float]) -> dict:
        result = {}
        
        if node_stabilities:
            result['avg_node_stability'] = np.mean(node_stabilities)
            result['min_node_stability'] = np.min(node_stabilities)
            result['node_stability_variance'] = np.var(node_stabilities)
        
        if link_stabilities:
            result['avg_link_stability'] = np.mean(link_stabilities)
            result['min_link_stability'] = np.min(link_stabilities)
            result['link_stability_variance'] = np.var(link_stabilities)
        
        if node_stabilities and link_stabilities:
            result['overall_stability'] = (
                result['avg_node_stability'] * 0.4 +
                result['avg_link_stability'] * 0.6  
            )
        elif link_stabilities:
            result['overall_stability'] = result['avg_link_stability']
        elif node_stabilities:
            result['overall_stability'] = result['avg_node_stability']
        else:
            result['overall_stability'] = 0.0
        
        return result