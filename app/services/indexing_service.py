import logging
import json
from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.services.metrics_service import metrics_tracker
from app.models.schemas import ExtractionResult, Entity, Relationship
from app.services.loader_service import Document

logger = logging.getLogger(__name__)

class IndexingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.MODEL_NAME_INDEXING # gpt-4o

    def _get_extraction_prompt(self, text: str) -> str:
        return f"""
ONTOLOGY:
- LABELS: Company, Person, Technology, Location, Product
- RELATIONSHIPS: FOUNDED_BY, WORKS_AT, CEO_OF, DEVELOPED, PARTNER_OF, INVESTED_IN, COMPETES_WITH, HEADQUARTERED_IN, ACQUIRED

INSTRUCTIONS:
1. Extract all relevant entities that match the LABELS.
2. Extract all relationships between these entities that match the RELATIONSHIPS.
3. For each entity, include a 'name' and its 'label'.
4. For each relationship, include 'source' (entity name), 'target' (entity name), and 'type'.
5. Output the result strictly as a valid JSON object with two keys: 'entities' and 'relationships'.
6. Do not include any explanation or preamble.

TEXT CHUNK:
\"\"\"
{text}
\"\"\"

JSON OUTPUT:
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_llm(self, prompt: str) -> str:
        """Helper to call LLM with retry logic."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a specialized Knowledge Graph Extraction agent. Your goal is to identify entities and relationships exactly as defined in the provided ontology and output them in the requested JSON structure. Be precise and avoid creating labels or relationship types that are not in the ontology."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0,
            seed=42,
            max_tokens=2000
        )
        # Update metrics (note: we update metrics even on retries, but the outer tracker captures total)
        # Actually, it's better to update metrics in the caller to avoid double counting or missing counts
        return response

    def extract_entities(self, chunk: Document) -> ExtractionResult:
        """Extracts entities and relationships from a text chunk using LLM with graceful validation."""
        prompt = self._get_extraction_prompt(chunk.page_content)
        
        with metrics_tracker.track("entity_extraction", model_name=self.model) as metrics:
            try:
                response = self._call_llm(prompt)
                
                content = response.choices[0].message.content
                data = json.loads(content)
                
                # Update metrics
                metrics["prompt_tokens"] = response.usage.prompt_tokens
                metrics["completion_tokens"] = response.usage.completion_tokens
                
                # Graceful validation
                valid_entities = []
                for e_data in data.get("entities", []):
                    try:
                        valid_entities.append(Entity.model_validate(e_data))
                    except Exception as e_val:
                        logger.warning(f"Skipping invalid entity in chunk {chunk.metadata.get('source_file')}: {str(e_val)}")
                
                valid_relationships = []
                for r_data in data.get("relationships", []):
                    try:
                        valid_relationships.append(Relationship.model_validate(r_data))
                    except Exception as r_val:
                        logger.warning(f"Skipping invalid relationship in chunk {chunk.metadata.get('source_file')}: {str(r_val)}")
                
                return ExtractionResult(entities=valid_entities, relationships=valid_relationships)
                
            except Exception as e:
                logger.error(f"Extraction failed for chunk {chunk.metadata.get('source_file')}: {str(e)}")
                return ExtractionResult(entities=[], relationships=[])

# Singleton instance
indexing_service = IndexingService()
