import logging
from typing import List, Dict, Any
from app.core.database import db
from app.models.schemas import Entity, Relationship
from app.models.ontology import Ontology

logger = logging.getLogger(__name__)

class Neo4jRepository:
    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        if not self._driver:
            self._driver = db.driver
        return self._driver

    def create_constraints(self):
        """Creates uniqueness constraints for entities and chunks."""
        # Note: Since we have multiple labels, we can't create one constraint for all
        # unless we add a base label ':BaseEntity' to everything.
        # For now, let's create constraints for each label in our Ontology.
        try:
            with self.driver.session() as session:
                for label in Ontology.LABELS:
                    query = f"CREATE CONSTRAINT {label.lower()}_name_unique IF NOT EXISTS FOR (n:{label}) REQUIRE n.name IS UNIQUE"
                    session.run(query)
                
                # Constraint for Chunks
                session.run("CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (n:Chunk) REQUIRE (n.chunk_id, n.source_file) IS UNIQUE")
                
            logger.info("Database constraints verified/created.")
        except Exception as e:
            logger.warning(f"Failed to create constraints (might already exist or not supported): {str(e)}")

    def create_vector_index(self, index_name: str, label: str, property: str, dimensions: int):
        """Creates a vector index if it doesn't exist."""
        query = f"""
        CREATE VECTOR INDEX {index_name} IF NOT EXISTS
        FOR (n:{label}) ON (n.{property})
        OPTIONS {{
          indexConfig: {{
            `vector.dimensions`: {dimensions},
            `vector.similarity_function`: 'cosine'
          }}
        }}
        """
        try:
            with self.driver.session() as session:
                session.run(query)
            logger.info(f"Vector index '{index_name}' verified/created.")
        except Exception as e:
            logger.error(f"Failed to create vector index: {str(e)}")
            raise e

    def merge_entities_batch(self, entities: List[Entity]):
        """Merges a list of entities using batching (UNWIND)."""
        if not entities:
            return
            
        def _merge_batch(tx, label, items):
            query = f"""
            UNWIND $items AS item
            MERGE (n:{label} {{name: item.name}})
            SET n += item.properties
            """
            tx.run(query, items=items)

        # Group by label for efficient UNWIND
        grouped = {}
        for e in entities:
            if e.label not in grouped: grouped[e.label] = []
            grouped[e.label].append({"name": e.name, "properties": e.properties})

        try:
            with self.driver.session() as session:
                for label, items in grouped.items():
                    session.execute_write(_merge_batch, label, items)
            logger.debug(f"Batch merged {len(entities)} entities.")
        except Exception as e:
            logger.error(f"Failed to batch merge entities: {str(e)}")
            raise e

    def merge_relationships_batch(self, relationships: List[Relationship]):
        """Merges a list of relationships using batching (UNWIND)."""
        if not relationships:
            return

        def _merge_rel_batch(tx, rel_type, items):
            query = f"""
            UNWIND $items AS item
            MATCH (s {{name: item.source}})
            MATCH (t {{name: item.target}})
            MERGE (s)-[r:{rel_type}]->(t)
            SET r += item.properties
            """
            tx.run(query, items=items)

        # Group by type
        grouped = {}
        for r in relationships:
            if r.type not in grouped: grouped[r.type] = []
            grouped[r.type].append({"source": r.source, "target": r.target, "properties": r.properties})

        try:
            with self.driver.session() as session:
                for rel_type, items in grouped.items():
                    session.execute_write(_merge_rel_batch, rel_type, items)
            logger.debug(f"Batch merged {len(relationships)} relationships.")
        except Exception as e:
            logger.error(f"Failed to batch merge relationships: {str(e)}")
            raise e

    def save_chunk_tx(self, text: str, embedding: List[float], metadata: Dict[str, Any], entities: List[Entity]):
        """Saves a text chunk and links it to entities within a transaction."""
        def _save_chunk(tx, text, embedding, metadata, entity_names):
            query = """
            MERGE (c:Chunk {chunk_id: $chunk_id, source_file: $source_file})
            SET c.text = $text, c.embedding = $embedding, c.file_path = $file_path
            WITH c
            UNWIND $entity_names AS entity_name
            MATCH (e {name: entity_name})
            MERGE (c)-[:MENTIONS]->(e)
            """
            tx.run(
                query,
                chunk_id=metadata.get("chunk_id"),
                source_file=metadata.get("source_file"),
                text=text,
                embedding=embedding,
                file_path=metadata.get("file_path"),
                entity_names=entity_names
            )

        try:
            entity_names = [e.name for e in entities]
            with self.driver.session() as session:
                session.execute_write(_save_chunk, text, embedding, metadata, entity_names)
        except Exception as e:
            logger.error(f"Failed to save chunk transactionally: {str(e)}")
            raise e

# Singleton instance
neo4j_repo = Neo4jRepository()
