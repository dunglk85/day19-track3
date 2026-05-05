# Phân tích chi phí xây dựng đồ thị tri thức (Indexing Cost Analysis)

Dựa trên quá trình xây dựng đồ thị tri thức cho tập dữ liệu **Tech Company Corpus** (~4.6 KB văn bản), dưới đây là phân tích chi tiết về chi phí sử dụng tài nguyên và thời gian.

## 1. Chi phí Token (Token Usage)
Hệ thống sử dụng mô hình **GPT-4o** cho giai đoạn trích xuất (Extraction) và **text-embedding-3-large** cho giai đoạn nhúng (Embedding).

| Hoạt động | Mô hình | Số lượng (Ước tính) | Chi phí đơn giá | Thành tiền (USD) |
|:---|:---|:---|:---|:---|
| **Trích xuất (Input)** | GPT-4o | 10,000 tokens | $5.00 / 1M tokens | $0.0500 |
| **Trích xuất (Output)** | GPT-4o | 2,500 tokens | $15.00 / 1M tokens | $0.0375 |
| **Embedding** | text-embedding-3-large | 2,000 tokens | $0.13 / 1M tokens | $0.0003 |
| **Tổng cộng** | | | | **~$0.0878** |

*Ghi chú: Chi phí thực tế có thể thay đổi nhẹ tùy thuộc vào số lượng thực thể/quan hệ được trích xuất từ mỗi chunk.*

## 2. Thời gian thực hiện (Time Performance)
Tổng thời gian để hoàn thành việc xây dựng đồ thị từ file văn bản thô đến khi lưu trữ hoàn tất trong Neo4j.

*   **Tải & Chia nhỏ văn bản (Loading & Chunking)**: < 1 giây.
*   **Trích xuất thực thể & quan hệ (LLM Extraction)**: 30 - 50 giây (Xử lý tuần tự các chunk).
*   **Tạo Embedding cho các Chunk**: 1 - 2 giây.
*   **Lưu trữ vào Neo4j (Cypher Execution)**: 2 - 3 giây.
*   **Tổng thời gian Indexing**: **~1 phút**.

## 3. Đánh giá & Nhận xét
*   **Ưu điểm**: Chi phí cực thấp (~2,200 VNĐ) cho một hệ thống tri thức chuyên sâu. Thời gian xử lý nhanh phù hợp với các tập dữ liệu quy mô vừa.
*   **Hạn chế**: Khi dữ liệu tăng lên hàng GB, chi phí LLM cho việc trích xuất sẽ trở nên đáng kể.
*   **Giải pháp tối ưu**: 
    1. Sử dụng các mô hình rẻ hơn (như GPT-4o-mini) cho các văn bản đơn giản.
    2. Xử lý song song (Parallel Processing) các chunk để giảm tổng thời gian chờ.
    3. Lưu bộ nhớ đệm (Caching) các kết quả trích xuất để tránh trùng lặp.

---
*Báo cáo được chuẩn bị cho Lab 19 - GraphRAG Pipeline.*
