from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeData:
    id: str
    type: str
    status: str
    cpu_load: float
    jitter_ms: float
    queue_len: int
    throughput_mbps: float
    last_updated: datetime


@dataclass
class LinkData:
    src: str
    dst: str
    available: bool
    delay_ms: float
    jitter_ms: float
    loss_rate: float
    bandwidth_mbps: float
    last_updated: datetime