## 🧩 1️⃣ Mục tiêu của heuristic module (cập nhật)

| Chức năng                                 | Mô tả                                                                  |
| ----------------------------------------- | ---------------------------------------------------------------------- |
| **1. Nhận dữ liệu mạng (graph)**          | Nhận snapshot từ backend qua gRPC (`UpdateGraph`)                      |
| **2. Build & cache graph nội bộ**         | Chuyển nodes/links → NetworkX weighted graph, lưu vào bộ nhớ           |
| **3. Chạy thuật toán heuristic**          | A*, Greedy, GA, SA… tính đường và score                                |
| **4. Tính ổn định mạng (stabilityScore)** | Dựa trên biến động delay, loss, jitter                                 |
| **5. Trả kết quả route**                  | Khi một node yêu cầu gửi gói tin (`RequestRoute`), trả về route tối ưu |
| **6. Theo dõi thời gian thực**            | Giữ graph hiện tại trong RAM bằng NumPy mảng adjacency                 |

---

## ⚙️ 2️⃣ Kiến trúc tổng thể

```
        ┌────────────────────────────────────────┐
        │          HEURISTIC MODULE              │
        │----------------------------------------│
        │ gRPC Server (grpc.aio)                 │
        │----------------------------------------│
        │ Graph Manager  (NetworkX + NumPy cache)│
        │----------------------------------------│
        │ Heuristic Engine (A*, GA, SA...)       │
        │----------------------------------------│
        │ Stability Analyzer (metrics smoothing) │
        └────────────────────────────────────────┘
```

---

## 🧱 3️⃣ Ngôn ngữ & Framework

| Thành phần                  | Lý do chọn                | Cụ thể                                                      |
| --------------------------- | ------------------------- | ----------------------------------------------------------- |
| **Ngôn ngữ:**               | Python 🐍                 | dễ code heuristic, dễ thao tác graph                        |
| **gRPC Framework:**         | `grpc.aio` (async-native) | hiệu năng cao, tương thích backend NestJS gRPC client       |
| **Graph Engine:**           | NetworkX + NumPy          | NetworkX cho route logic, NumPy cho lưu ma trận & stability |
| **Heuristic/Optimization:** | PyGAD hoặc custom A*, SA  | linh hoạt                                                   |
| **Logging:**                | loguru                    | log pipeline gọn, dễ đọc                                    |

---

## 🧠 4️⃣ Kiến trúc thư mục gọn (gRPC version)

```
heuristic-module/
│
├── app/
│   ├── main.py                # Entrypoint (start gRPC server)
│   ├── proto/
│   │   └── heuristic.proto    # định nghĩa service gRPC
│   ├── services/
│   │   ├── heuristic_service.py # gRPC service: UpdateGraph, RequestRoute
│   │   ├── graph_manager.py     # Quản lý graph NetworkX + NumPy
│   │   ├── heuristic_engine.py  # A*, GA, SA,...
│   │   └── stability.py         # Tính stabilityScore
│   └── utils/
│       └── logger.py            # loguru config
│
├── requirements.txt
└── Dockerfile
```

---

## 📦 5️⃣ requirements.txt

```txt
grpcio==1.65.4
grpcio-tools==1.65.4
networkx==3.3
numpy==1.26.4
loguru==0.7.2
```

---

## 🚀 8️⃣ Dòng hoạt động tổng thể

```
(Backend)
  └──> gRPC call: UpdateGraph(GraphSnapshot)
           ↓
     HeuristicService.UpdateGraph()
           ↓
     GraphManager.build(NetworkX + NumPy)
           ↓
  (Graph stored in memory)

(Node / Backend)
  └──> gRPC call: RequestRoute(src, dst)
           ↓
     HeuristicEngine.A*(G, src, dst)
           ↓
     Return { route, total_weight, stability_score }
```

---