from neo4j import GraphDatabase
from app.core.config import settings
import logging
import threading
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    def __init__(self):
        self._driver = None
        self._lock = threading.Lock()

    def connect(self):
        """Initializes the Neo4j driver with thread safety."""
        if not self._driver:
            with self._lock:
                # Double-check pattern
                if not self._driver:
                    try:
                        self._driver = GraphDatabase.driver(
                            settings.NEO4J_URI,
                            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
                        )
                        # Verify connectivity
                        self._driver.verify_connectivity()
                        logger.info("Successfully connected to Neo4j")
                    except Exception as e:
                        logger.error(f"Failed to connect to Neo4j: {str(e)}")
                        self._driver = None
                        raise e

    def close(self):
        """Closes the Neo4j driver."""
        with self._lock:
            if self._driver:
                self._driver.close()
                self._driver = None
                logger.info("Neo4j driver closed")

    @property
    def driver(self):
        """Returns the Neo4j driver instance."""
        if not self._driver:
            self.connect()
        return self._driver

    def _sync_check_health(self) -> bool:
        """Internal synchronous health check."""
        if not self._driver:
            try:
                self.connect()
            except:
                return False
        
        try:
            with self._driver.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {str(e)}")
            return False

    async def check_health(self) -> bool:
        """Performs a non-blocking connectivity check."""
        return await run_in_threadpool(self._sync_check_health)

    def _sync_check_vector_health(self) -> bool:
        """Internal synchronous vector index check."""
        if not self._driver:
            return False
        try:
            with self._driver.session() as session:
                # Check if Neo4j version supports Vector or if any vector index exists
                # For 1.2, we just check if the database responds to a simple index query
                result = session.run("SHOW INDEXES YIELD type WHERE type = 'VECTOR' RETURN count(*) > 0 as exists").single()
                return result["exists"] if result else False
        except Exception as e:
            # If the command is not supported (old Neo4j), it's not "healthy" for our GraphRAG
            logger.warning(f"Vector capability check failed or not supported: {str(e)}")
            return False

    async def check_vector_health(self) -> bool:
        """Performs a non-blocking vector capability check."""
        return await run_in_threadpool(self._sync_check_vector_health)

# Create a singleton instance
db = Neo4jDatabase()
