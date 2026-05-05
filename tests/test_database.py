import pytest
from app.core.database import Neo4jDatabase
from unittest.mock import MagicMock, patch
import asyncio

@patch("app.core.database.GraphDatabase")
def test_neo4j_connection_success(mock_graph_db):
    # Setup mock
    mock_driver = MagicMock()
    mock_graph_db.driver.return_value = mock_driver
    
    db = Neo4jDatabase()
    db.connect()
    
    assert db._driver is not None
    mock_graph_db.driver.assert_called_once()
    mock_driver.verify_connectivity.assert_called_once()

@patch("app.core.database.GraphDatabase")
def test_neo4j_connection_failure(mock_graph_db):
    # Setup mock to raise exception
    mock_graph_db.driver.side_effect = Exception("Connection failed")
    
    db = Neo4jDatabase()
    with pytest.raises(Exception):
        db.connect()
    
    assert db._driver is None

@pytest.mark.asyncio
@patch("app.core.database.GraphDatabase")
async def test_neo4j_health_check_success(mock_graph_db):
    # Setup mock
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_graph_db.driver.return_value = mock_driver
    
    db = Neo4jDatabase()
    db._driver = mock_driver
    
    result = await db.check_health()
    
    assert result is True
    mock_session.run.assert_called_with("RETURN 1")

@pytest.mark.asyncio
@patch("app.core.database.GraphDatabase")
async def test_neo4j_vector_health_check(mock_graph_db):
    # Setup mock
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.__getitem__.return_value = True
    mock_session.run.return_value.single.return_value = mock_result
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    db = Neo4jDatabase()
    db._driver = mock_driver
    
    result = await db.check_vector_health()
    
    assert result is True
    # Verify the query checks for VECTOR indexes
    args, kwargs = mock_session.run.call_args
    assert "type = 'VECTOR'" in args[0]
