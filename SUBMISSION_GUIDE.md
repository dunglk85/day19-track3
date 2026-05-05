# 📘 Hướng dẫn Hoàn thiện & Nộp bài Lab 19 (GraphRAG)

Tài liệu này hướng dẫn Admin cách vận hành hệ thống để thu thập đầy đủ các hạng mục cần thiết cho bài nộp Lab 19.

---

## 🛠️ 1. Quy trình thực thi hệ thống (Workflow)

Để tạo ra các báo cáo và dữ liệu cần thiết, Admin vui lòng thực hiện theo các bước sau:

1.  **Khởi động Cơ sở dữ liệu**: Chạy lệnh `docker-compose up -d` để khởi động Neo4j.
2.  **Chạy Server ứng dụng**: Thực thi `python main.py`.
3.  **Nạp dữ liệu & Xây dựng Đồ thị (Indexing)**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/indexing/load
    ```
4.  **Chạy Đánh giá Benchmark**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/benchmark/run
    ```
    *(Đợi khoảng 2-3 phút để hệ thống hoàn thành 20 câu hỏi).*
5.  **Xuất Báo cáo Tổng hợp**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/report/export-latest
    ```

---

## 📋 2. Danh sách Sản phẩm Bàn giao (Deliverables)

Dưới đây là 4 hạng mục bắt buộc phải có trong bài nộp:

### 📁 2.1. Mã nguồn (Source Code)
*   **Vị trí**: Toàn bộ thư mục gốc `day19-track3/`.
*   **Cách đóng gói**: Nén (zip) toàn bộ thư mục. 
*   **Lưu ý**: Loại bỏ các thư mục `.venv`, `neo4j/data` và `__pycache__` để giảm dung lượng file nộp.

### 📊 2.2. Ảnh chụp màn hình Đồ thị tri thức (KG Screenshot)
Admin có thể lấy hình ảnh này bằng 2 cách:
*   **Tự động**: Mở file báo cáo tại `submissions/reports/final_report_*.md`, sao chép mã **Mermaid** và dán vào [Mermaid Live Editor](https://mermaid.live/) để xuất ảnh.
*   **Trực tiếp**: Truy cập `http://localhost:7474`, chạy lệnh Cypher `MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50` và chụp ảnh giao diện.
*   **Lưu file**: Lưu vào `submissions/dothi_trithuc.png`.

### 📈 2.3. Bảng so sánh 20 câu hỏi Benchmark
*   **Vị trí**: File `submissions/benchmark_comparison.md`.
*   **Nội dung**: So sánh chi tiết kết quả giữa **Flat RAG** (Vector) và **GraphRAG** (Đồ thị) về độ chính xác và ngữ cảnh.

### 💰 2.4. Phân tích Chi phí & Hiệu năng
*   **Vị trí**: File `submissions/cost_analysis.md`.
*   **Thông tin cần thiết**: 
    *   **Token Usage**: Tổng lượng token tiêu thụ (xem trong file báo cáo).
    *   **Latency**: Thời gian phản hồi trung bình và P95.

---

## 📂 3. Cấu trúc Thư mục Submissions Tiêu chuẩn

Bài nộp của Admin nên được tổ chức như sau:

```text
submissions/
├── reports/                # Chứa các báo cáo .md tự động (final_report_*.md)
├── benchmark-results/      # Dữ liệu JSON thô từ quá trình chạy benchmark
├── benchmark_comparison.md # Bảng so sánh kết quả (Deliverable 2.3)
├── cost_analysis.md       # Báo cáo chi phí & hiệu năng (Deliverable 2.4)
└── dothi_trithuc.png       # Ảnh chụp đồ thị tri thức (Deliverable 2.2)
```

---

**Chúc Admin đạt điểm tối đa cho bài Lab 19!** 🚀

