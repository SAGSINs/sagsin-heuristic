from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetricSnapshot:
    timestamp: datetime
    value: float


@dataclass
class StabilityMetrics:
    mean: float
    variance: float
    std_deviation: float
    coefficient_of_variation: float  
    trend: float 
    stability_score: float 


class MetricsCalculator:
    @staticmethod
    def calculate_stability_score(cv: float, abs_trend: float, mean: float) -> float:
        cv_score = max(0.0, 1.0 - (cv / 2.0))
        
        relative_trend = abs_trend / (mean + 0.001) 
        trend_score = max(0.0, 1.0 - (relative_trend * 10.0))
        
        stability_score = 0.6 * cv_score + 0.4 * trend_score
        
        return min(1.0, max(0.0, stability_score))
    
    @staticmethod
    def detect_anomalies(snapshots: List[MetricSnapshot], mean: float, std_dev: float, threshold: float = 3.0) -> List[MetricSnapshot]:
        anomalies = []
        
        for snapshot in snapshots:
            z_score = abs(snapshot.value - mean) / (std_dev + 0.001)
            if z_score > threshold:
                anomalies.append(snapshot)
        
        return anomalies