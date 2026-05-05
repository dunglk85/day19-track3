# Hướng dẫn hoàn thiện Deliverables - Lab 19 (GraphRAG)

Tài liệu này hướng dẫn Admin cách chạy toàn bộ hệ thống để thu thập đầy đủ 4 hạng mục cần thiết cho bài nộp Lab 19.

---

## 🏗️ 1. Mã nguồn (Source Code)
Mã nguồn đã được tổ chức theo cấu trúc chuẩn FastAPI. 
- **Cách đóng gói**: Admin chỉ cần nén (zip) toàn bộ thư mục `day19-track3` (loại bỏ thư mục `.venv`, `neo4j/data` và `__pycache__` để giảm dung lượng).
- **Lưu ý**: Đảm bảo file `requirements.txt` và `.env.example` có đầy đủ thông tin.

## 📊 2. Ảnh chụp màn hình Đồ thị tri thức (KG Screenshot)
Admin có 2 cách để lấy hình ảnh này:
- **Cách 1 (Tự động)**: Mở file báo cáo tại `reports/final_report_*.md`. Tại đây có sẵn mã **Mermaid**. Admin có thể copy mã này vào [Mermaid Live Editor](https://mermaid.live/) để xuất ra ảnh PNG/SVG chất lượng cao.
- **Cách 2 (Trực tiếp từ Neo4j)**:
    1. Truy cập `http://localhost:7474` (Neo4j Browser).
    2. Chạy lệnh Cypher: `MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50`.
    3. Sử dụng tính năng hiển thị đồ thị của Neo4j và chụp ảnh màn hình.

## 📈 3. Bảng so sánh 20 câu hỏi Benchmark
Hệ thống đã tự động hóa quy trình này. Admin thực hiện theo các bước sau:

1. **Khởi chạy ứng dụng**: `python main.py`
2. **Nạp dữ liệu (Indexing)**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/indexing/load
   ```
3. **Chạy Benchmark**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/benchmark/run
   ```
   *(Đợi khoảng 2-3 phút để hệ thống chạy xong 20 câu hỏi).*
4. **Xuất báo cáo tổng hợp**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/report/export-latest
   ```
5. **Kết quả**: Mở file mới nhất trong thư mục `reports/`. Bảng so sánh nằm ở mục **"2. Performance Analytics"**.

## 💰 4. Phân tích chi phí (Token & Time)
Thông tin này cũng đã được tự động tổng hợp trong file báo cáo ở bước trên:
- **Token Usage**: Xem cột "Total Tokens" trong bảng so sánh.
- **Time**: Xem cột "Mean Latency" và "P95 Latency".
- **Phân tích ngắn**: Xem mục **"4. Conclusion & Insights"** trong file báo cáo để lấy các nhận định mẫu về chi phí và hiệu năng.

---

### 🛠️ Quy trình tóm tắt (Workflow)
1. `docker-compose up -d` (Chạy Neo4j)
2. `python main.py` (Chạy Server)
3. `curl .../indexing/load` (Tạo đồ thị)
4. `curl .../benchmark/run` (Đo lường)
5. `curl .../report/export-latest` (Lấy kết quả nộp bài)

**Chúc Admin đạt điểm tối đa!** 🚀
