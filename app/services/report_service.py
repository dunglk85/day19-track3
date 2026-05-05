import os
import json
from datetime import datetime
from typing import Dict, Any, List
from app.core.database import db
from app.services.analytics_service import analytics_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)

    async def get_graph_mermaid(self, limit: int = 25) -> str:
        """
        Extracts sample graph structure from Neo4j and formats it for Mermaid.
        """
        query = """
        MATCH (n)-[r]->(m)
        RETURN n.name as source, type(r) as rel, m.name as target
        LIMIT $limit
        """
        try:
            with db.driver.session() as session:
                result = session.run(query, limit=limit)
                records = result.data()
            
            mermaid = "graph TD\n"
            added_edges = set()
            for rec in records:
                # Sanitize names for Mermaid (remove spaces and special chars)
                source = str(rec["source"]).replace(" ", "_").replace("-", "_").replace(".", "_").replace("\"", "")
                target = str(rec["target"]).replace(" ", "_").replace("-", "_").replace(".", "_").replace("\"", "")
                rel = rec["rel"]
                
                edge = f"{source}--{rel}-->{target}"
                if edge not in added_edges:
                    mermaid += f"    {source} -- {rel} --> {target}\n"
                    added_edges.add(edge)
            
            if not added_edges:
                return "graph TD\n    No_Data -- In_Database --> Graph"
                
            return mermaid
        except Exception as e:
            logger.error(f"Failed to extract graph for Mermaid: {str(e)}")
            return f"graph TD\n    Error -- {str(e).replace(' ', '_')} --> Graph"

    async def generate_final_report(self, benchmark_file: str) -> str:
        """
        Synthesizes all data into a final_report.md.
        """
        # 1. Get analytics data
        analytics = analytics_service.analyze_file(benchmark_file)
        if not analytics or analytics.get("status") == "error":
            logger.error(f"Cannot generate report: Analytics failed for {benchmark_file}")
            return ""

        # 2. Get graph visualization (Mermaid)
        mermaid_graph = await self.get_graph_mermaid(30)

        # 3. Assemble Markdown
        timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_md = f"""# Final Lab Report: Hybrid GraphRAG Evaluation

**Dự án**: Tech Company Corpus RAG Pipeline
**Ngày xuất báo cáo**: {timestamp_now}
**Tập dữ liệu**: {analytics['summary']['file']}

## 1. Kiến trúc Hệ thống (System Architecture)
Hệ thống sử dụng phương pháp **Hybrid Retrieval**, kết hợp giữa tìm kiếm Vector (Semantic) và duyệt Đồ thị tri thức (Structural).

### Sơ đồ Đồ thị tri thức (Mẫu 30 quan hệ đầu tiên)
```mermaid
{mermaid_graph}
```

## 2. Phân tích Hiệu năng (Performance Analytics)

| Chỉ số (Metric) | Vector RAG (Baseline) | Hybrid GraphRAG | Chênh lệch (%) |
|---|---|---|---|
| **Mean Latency** | {analytics['vector']['latency']['mean']}ms | {analytics['hybrid']['latency']['mean']}ms | {analytics['comparison']['latency_increase_pct']}% |
| **P95 Latency** | {analytics['vector']['latency']['p95']}ms | {analytics['hybrid']['latency']['p95']}ms | - |
| **Total Tokens** | {analytics['vector']['tokens']['total']} | {analytics['hybrid']['tokens']['total']} | - |
| **Estimated Cost (USD)** | ${analytics['vector']['cost_usd']} | ${analytics['hybrid']['cost_usd']} | {analytics['comparison']['cost_increase_pct']}% |

## 3. Đánh giá Định tính (Qualitative Findings)
- **Vector RAG**: Hoạt động tốt với các câu hỏi tra cứu thông tin trực tiếp (Simple Retrieval). Latency thấp nhưng gặp khó khăn khi câu hỏi yêu cầu kết nối nhiều thực thể không nằm cạnh nhau trong văn bản.
- **Hybrid GraphRAG**: Tỏa sáng với các câu hỏi đa bước (Multi-hop). Khả năng trích xuất mối quan hệ từ Neo4j giúp câu trả lời có độ chính xác cao hơn về mặt cấu trúc thực thể và quan hệ sở hữu/phát triển.

## 4. Kết luận & Đề xuất (Conclusion & Insights)
- **Kết luận**: GraphRAG làm tăng chi phí token và độ trễ (khoảng {analytics['comparison']['latency_increase_pct']}%) nhưng bù lại cung cấp ngữ cảnh phong phú và chính xác hơn cho các truy vấn phức tạp về quan hệ.
- **Đề xuất**: 
    1. Sử dụng **Hybrid RAG** cho các hệ thống quản trị tri thức chuyên sâu, nghiên cứu thị trường và phân tích đối thủ.
    2. Sử dụng **Vector RAG** cho các tác vụ hỏi đáp FAQ đơn giản hoặc chatbot hỗ trợ khách hàng thông thường để tối ưu chi phí.

---
*Báo cáo được tạo tự động bởi ReportService.*
"""
        
        # Save report
        report_filename = f"final_report_{analytics['summary']['timestamp']}.md"
        output_path = os.path.join(self.reports_dir, report_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_md)
            
        logger.info(f"Final report generated at {output_path}")
        return output_path

report_service = ReportService()
