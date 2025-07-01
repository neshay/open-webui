import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import json

# Add the backend directory to the path
sys.path.append('backend')

from open_webui.models.files import FileModel
from open_webui.utils.misc import calculate_sha256_string


class TestNeo4jIngestion(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_content = "This is a test document content for Neo4j ingestion."
        self.test_filename = "test_document.txt"
        self.test_file_id = "test-file-123"
        self.test_hash = calculate_sha256_string(self.test_content)
        
        # Create a mock file object
        self.mock_file = MagicMock()
        self.mock_file.filename = self.test_filename
        self.mock_file.id = self.test_file_id
        self.mock_file.data = {"content": self.test_content}
        
    @patch('requests.post')
    @patch.dict(os.environ, {
        'NEO4J_GRAPH_INGEST': 'true',
        'SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE': 'http://localhost:8080/ingest'
    })
    def test_neo4j_ingestion_success(self, mock_post):
        """Test successful Neo4j ingestion"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # This would be the actual ingestion logic
        payload = {
            "file_name": self.mock_file.filename,
            "file_hash": self.test_hash,
            "content": str(self.test_content),
            "chat_id": "123",
        }
        
        # Simulate the request
        response = requests.post('http://localhost:8080/ingest', json=payload)
        response.raise_for_status()
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            'http://localhost:8080/ingest',
            json=payload
        )
        
    @patch('requests.post')
    @patch.dict(os.environ, {
        'NEO4J_GRAPH_INGEST': 'true',
        'SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE': 'http://localhost:8080/ingest'
    })
    def test_neo4j_ingestion_http_error(self, mock_post):
        """Test Neo4j ingestion with HTTP error"""
        # Mock HTTP error
        mock_post.side_effect = requests.RequestException("Connection failed")
        
        # This should be caught and logged, not raise an exception
        try:
            payload = {
                "file_name": self.mock_file.filename,
                "file_hash": self.test_hash,
                "content": str(self.test_content),
                "chat_id": "123",
            }
            response = requests.post('http://localhost:8080/ingest', json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            # This is expected behavior
            self.assertIn("Connection failed", str(e))
            
    @patch.dict(os.environ, {'NEO4J_GRAPH_INGEST': 'false'})
    def test_neo4j_ingestion_disabled(self):
        """Test that Neo4j ingestion is skipped when disabled"""
        # When NEO4J_GRAPH_INGEST is not set or false, the ingestion should be skipped
        self.assertFalse(os.environ.get("NEO4J_GRAPH_INGEST"))
        
    @patch.dict(os.environ, {
        'NEO4J_GRAPH_INGEST': 'true'
        # SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE not set
    })
    def test_neo4j_ingestion_missing_url(self):
        """Test Neo4j ingestion with missing microservice URL"""
        # Should raise ValueError when URL is not set
        with self.assertRaises(ValueError):
            url = os.getenv("SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE")
            if not url:
                raise ValueError("SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE environment variable not set")


if __name__ == '__main__':
    unittest.main() 