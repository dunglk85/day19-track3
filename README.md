# Tech Company Corpus GraphRAG Pipeline

Hệ thống RAG (Retrieval-Augmented Generation) tiên tiến kết hợp giữa tìm kiếm Vector truyền thống và Đồ thị tri thức (Knowledge Graph) để cung cấp câu trả lời chính xác, có ngữ cảnh sâu về các công ty công nghệ.

## 🌟 Tính năng nổi bật

- **Hybrid Search Engine**: Kết hợp sức mạnh của Semantic Search (Vector) và Structural Traversal (Graph) để trả lời các câu hỏi phức tạp.
- **Automated KG Construction**: Tự động trích xuất thực thể và mối quan hệ từ văn bản bằng GPT-4o.
- **Multi-hop Retrieval**: Duyệt đồ thị 2-hop để tìm kiếm các mối liên kết giấu kín giữa các công ty và công nghệ.
- **Benchmark & Analytics**: Tự động chạy khảo sát 20 câu hỏi, đo lường Latency và tính toán chi phí Token thực tế.
- **Automated Reporting**: Xuất báo cáo Lab Report chuyên nghiệp với sơ đồ Mermaid trực quan.

## 🛠️ Công nghệ sử dụng

- **Backend**: FastAPI (Python 3.11+)
- **Database**: Neo4j (Graph Database & Vector Index)
- **AI Models**: 
  - GPT-4o (Indexing/Extraction)
  - GPT-4o-mini (Generation/Synthesis)
  - text-embedding-3-large (Embeddings)
- **Retriever**: `neo4j-graphrag` (VectorCypherRetriever)
- **Testing**: PyTest

## 📋 Yêu cầu hệ thống

- **Python**: 3.10 trở lên.
- **Neo4j**: Phiên bản 5.x trở lên (Cài đặt plugin **APOC** và **GDS** nếu cần).
- **OpenAI API Key**: Cần có số dư để thực hiện các cuộc gọi LLM.

## 🚀 Cài đặt & Thiết lập

### 1. Clone dự án
```bash
git clone <repository-url>
cd day19-track3
```

### 2. Thiết lập môi trường ảo
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc và điền các thông tin sau:
```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# App
PORT=8000
DEBUG=True
```

## 📖 Hướng dẫn sử dụng

### 1. Khởi chạy Server
```bash
python main.py
```
Truy cập tài liệu API tại: `http://localhost:8000/docs`

### 2. Đổ dữ liệu & Indexing (Epic 2)
Sử dụng endpoint `/api/v1/indexing/load` để nạp dữ liệu văn bản và xây dựng đồ thị tri thức.

### 3. Tìm kiếm (Epic 3)
Gửi yêu cầu đến `/api/v1/search/query`:
- **Vector Search**: `{"query": "...", "method": "vector"}`
- **Hybrid Search**: `{"query": "...", "method": "hybrid"}`

### 4. Chạy Benchmark & Báo cáo (Epic 4)
1. **Chạy 20 câu hỏi**: `POST /api/v1/benchmark/run`
2. **Xem phân tích chi phí**: `GET /api/v1/analytics/latest`
3. **Xuất báo cáo cuối cùng**: `POST /api/v1/report/export-latest`

Báo cáo sẽ được lưu tại: `reports/final_report_*.md`

## 🧪 Kiểm thử (Testing)
Chạy toàn bộ bộ test để đảm bảo hệ thống ổn định:
```bash
pytest
```

## 📂 Cấu trúc dự án
- `app/api/`: Các endpoint API (v1).
- `app/services/`: Logic nghiệp vụ (Search, Indexing, Analytics, Report).
- `app/core/`: Cấu hình hệ thống và kết nối Database.
- `app/models/`: Pydantic schemas và Ontology.
- `_bmad-output/`: Kết quả benchmark và báo cáo.

---
**Dự án được phát triển bởi Antigravity AI Assistant.** 🚀
