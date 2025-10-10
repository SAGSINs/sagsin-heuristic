Quick instructions to run the minimal Heuristic gRPC server locally (prints incoming GraphSnapshot)

1) Activate your existing virtualenv (.venv) and install deps:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Generate python gRPC stubs (from repo root):

```powershell
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/heuristic.proto
```

This will create `proto/heuristic_pb2.py` and `proto/heuristic_pb2_grpc.py` inside `proto/`.

3) Run the server:

```powershell
python -m app.main
```

The server listens on port 50051 by default and will print received snapshots to stdout.
