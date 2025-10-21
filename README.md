# SAGSIN Heuristic Service

Python gRPC service cung cấp route optimization và network stability analysis cho hệ thống SAGSIN.

## 🎯 Giới Thiệu

SAGSIN Heuristic Service là microservice tính toán routing tối ưu trong mạng phân tán:
- **Route Optimization**: A*, Dijkstra, Greedy algorithms
- **Stability Analysis**: Real-time network stability scoring
- **Graph Management**: NetworkX + NumPy caching
- **gRPC API**: UpdateGraph và RequestRoute services
- **Socket.IO**: Real-time algorithm streaming

## 🏗️ Kiến Trúc

```
sagsin-heuristic/
├── app/
│   ├── main.py                # Entry point - gRPC server
│   │
│   ├── services/              # Service layer
│   │   ├── heuristic_service.py    # gRPC handlers
│   │   └── heuristic_engine.py     # Orchestration
│   │
│   ├── core/                  # Core logic
│   │   └── graph/             # Graph management
│   │       ├── graph_manager.py         # Coordinator
│   │       ├── graph_operations.py      # NetworkX ops
│   │       ├── adjacency_manager.py     # NumPy cache
│   │       ├── graph_stats.py           # Metrics
│   │       └── data_structures.py       # Models
│   │
│   ├── algorithms/            # Pathfinding
│   │   ├── base.py           # Base algorithm
│   │   ├── astar.py          # A* heuristic
│   │   ├── dijkstra.py       # Dijkstra shortest
│   │   └── greedy.py         # Greedy best-first
│   │
│   ├── analysis/              # Stability
│   │   ├── stability_analyzer.py       # Coordinator
│   │   ├── history_manager.py          # Metrics history
│   │   ├── stability_calculator.py     # Calculations
│   │   └── metrics.py                  # Data models
│   │
│   └── utils/
│       └── logger.py          # Logging
│
├── proto/                     # Protocol Buffers
│   ├── heuristic.proto       # Route service
│   └── algorithm_stream.proto # Real-time stream
│
├── Dockerfile                 # Multi-stage build
├── requirements.txt           # Dependencies
└── PROJECT_OVERVIEW.md       # Detailed docs
```
### Routing Algorithms

**A* Algorithm**
- Network-aware heuristic với delay/bandwidth
- Best cho balance giữa speed và optimality
- Complexity: O(V log V)

**Dijkstra Algorithm**
- Classic shortest path, guaranteed optimal
- Best cho reliability-critical routes
- Complexity: O((V + E) log V)

**Greedy Algorithm**
- Best-first search cho real-time performance
- Fastest response time
- Complexity: O(V + E)

### Route Metrics

Mỗi route calculation trả về:
- **Path**: List of node hops
- **Total Delay**: Sum of link delays (ms)
- **Jitter**: Average jitter across path (ms)
- **Loss Rate**: Maximum loss rate (%)
- **Bandwidth**: Minimum bandwidth (Mbps)
- **Hop Count**: Number of hops
- **Stability Score**: Path stability rating

## 🚀 Hướng Dẫn Chạy

### Development

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate gRPC code
python -m grpc_tools.protoc -I./proto \
  --python_out=./proto \
  --grpc_python_out=./proto \
  ./proto/heuristic.proto \
  ./proto/algorithm_stream.proto

# Run server
python -m app.main
```

### Docker (Production)

```bash
# Build image
docker build -t sagsin-heuristic .
```

## 📊 Kết Quả Đạt Được

### ✅ Core Features

1. **Multi-Algorithm Support**: 3 routing algorithms với trade-offs khác nhau
2. **Real-time Updates**: Graph updates mỗi 3-5 giây từ backend
3. **Stability Analysis**: Network-wide stability monitoring
4. **High Performance**: Sub-millisecond route calculations
5. **Scalability**: Support networks với thousands of nodes
6. **Thread Safety**: Concurrent graph operations
7. **Comprehensive Metrics**: 7 route metrics cho informed decisions

### 📈 Performance

- **Route Calculation**: <1ms cho typical network (15 nodes)
- **Graph Update**: <50ms cho full rebuild
- **Memory Usage**: ~50-100MB baseline
- **Throughput**: 1000+ route requests/second
- **Concurrent Clients**: Support multiple agents simultaneously
- **Network Size**: Tested với 1000+ nodes

### 🔍 Graph Management

**NetworkX Integration**:
```python
- Flexible graph data structure
- Built-in algorithms và metrics
- Node/link attribute storage
- Centrality calculations
```

**NumPy Caching**:
```python
- O(1) adjacency matrix lookups
- Fast path calculations
- Memory-efficient storage
- Automatic cache invalidation
```

**Statistics Tracking**:
```python
- Node count, link count
- Average degree, density
- Connected components
- Centrality metrics
```

### 📊 Stability Analysis

**Metrics Tracking**:
- Sliding window history (configurable size)
- Exponential moving averages
- Coefficient of variation
- Node/link stability scores

**Calculations**:
- Real-time stability updates
- Historical trend analysis
- Anomaly detection
- Network-wide aggregation

### 🔧 Integration Points

**Backend Integration**:
- Receives GraphSnapshot updates via gRPC
- Updates mỗi 3-5 giây
- Graceful degradation nếu updates fail

**Agent Integration**:
- RequestRoute gRPC calls
- Multiple algorithms selection
- Comprehensive route responses
- Load balancing support

**Socket.IO Streaming**:
- Real-time algorithm execution updates
- Step-by-step pathfinding visualization
- Performance metrics streaming

## 🛠️ Development Tools

## 📝 Notes

- Python 3.11 với async/await patterns
- gRPC async server cho high concurrency
- NetworkX 3.3 cho graph operations
- NumPy cho matrix calculations
- Loguru cho structured logging
- Protocol Buffers cho efficient serialization
- Thread-safe graph updates
- Comprehensive error handling
- Performance monitoring built-in

---

**Tech Stack**: Python 3.11, gRPC, NetworkX, NumPy, Socket.IO  
**Docker Hub**: `baocules/sagsin-heuristic`  
**Port**: 50052 (gRPC)
