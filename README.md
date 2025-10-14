# Heuristic Module for SAGSINs Network

Complete implementation of the heuristic module for network route optimization and stability analysis.

## 🏗️ Architecture Components

- **Graph Manager**: NetworkX + NumPy graph management and caching
- **Heuristic Engine**: A*, Dijkstra, and Greedy pathfinding algorithms  
- **Stability Analyzer**: Real-time network stability scoring and metrics smoothing
- **gRPC Service**: Async server handling UpdateGraph and RequestRoute RPCs

## 📦 Dependencies

Install all dependencies:

```powershell
pip install -r requirements.txt

## 🔧 Setup Instructions

1. **Activate virtual environment:**
```powershell
.\.venv\Scripts\Activate.ps1
```

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Generate Python gRPC stubs:**
```powershell
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/heuristic.proto
```

4. **Run the server:**
```powershell
python -m app.main
```

## 🚀 Running the Service
### Docker Deployment
```powershell
# Build image
docker build -t sagsin-heuristic:latest .

# Run container
docker run --rm -p 50052:50052 sagsin-heuristic:latest
```

## 🔧 Configuration

Environment variables:
- `HEURISTIC_LISTEN`: Server listen address (default: "0.0.0.0:50052")
- `LOG_LEVEL`: Logging level (default: "INFO")
- `LOG_FILE`: Optional log file path
- `JSON_LOGS`: Use JSON log format (default: "false")
