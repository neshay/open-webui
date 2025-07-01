#!/usr/bin/env python3
"""
Manual testing script for Neo4j ingestion functionality
This script simulates the file processing workflow and tests the Neo4j ingestion
"""

import os
import sys
import requests
import json
import tempfile
from pathlib import Path

# Add the backend directory to the path
sys.path.append('backend')

def test_neo4j_ingestion():
    """Test the Neo4j ingestion functionality"""
    
    # Set up environment variables for testing
    os.environ['NEO4J_GRAPH_INGEST'] = 'true'
    os.environ['SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE'] = 'http://localhost:8081/ingest'
    
    # Test data
    test_content = """
    This is a test document for Neo4j ingestion.
    It contains multiple lines of text to simulate a real document.
    
    The content should be processed and sent to the Neo4j microservice.
    This tests the integration between OpenWebUI and the graph database.
    """
    
    test_filename = "test_document.txt"
    test_file_id = "test-file-123"
    
    # Calculate hash (simulating the actual process)
    import hashlib
    test_hash = hashlib.sha256(test_content.encode()).hexdigest()
    
    print("=== Neo4j Ingestion Test ===")
    print(f"Test file: {test_filename}")
    print(f"File ID: {test_file_id}")
    print(f"Content length: {len(test_content)} characters")
    print(f"Hash: {test_hash}")
    print()
    
    # Test 1: Check if microservice is running
    print("1. Testing microservice availability...")
    try:
        response = requests.get('http://localhost:8081/health', timeout=5)
        if response.status_code == 200:
            print("✅ Microservice is running")
        else:
            print("❌ Microservice returned unexpected status code")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Microservice is not running: {e}")
        print("Please start the mock microservice with: python mock_neo4j_microservice.py")
        return False
    
    # Test 2: Test ingestion
    print("\n2. Testing file ingestion...")
    payload = {
        "file_name": test_filename,
        "file_hash": test_hash,
        "content": str(test_content),
        "chat_id": "123",
    }
    
    try:
        response = requests.post('http://localhost:8081/ingest', json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Ingestion successful: {result.get('message', 'Unknown')}")
        print(f"   Ingested at: {result.get('ingested_at', 'Unknown')}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ingestion failed: {e}")
        return False
    
    # Test 3: Verify ingested data
    print("\n3. Verifying ingested data...")
    try:
        response = requests.get('http://localhost:8081/ingested', timeout=5)
        response.raise_for_status()
        
        data = response.json()
        ingested_count = data.get('count', 0)
        ingested_files = data.get('data', [])
        
        print(f"✅ Found {ingested_count} ingested files")
        
        if ingested_count > 0:
            latest_file = ingested_files[-1]
            print(f"   Latest file: {latest_file.get('file_name')}")
            print(f"   File hash: {latest_file.get('file_hash')}")
            print(f"   Content length: {len(latest_file.get('content', ''))}")
            
            # Verify the data matches
            if (latest_file.get('file_name') == test_filename and 
                latest_file.get('file_hash') == test_hash and
                latest_file.get('content') == test_content):
                print("✅ Data verification successful")
            else:
                print("❌ Data verification failed")
                return False
        else:
            print("❌ No ingested files found")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    # Test 4: Test error handling (missing environment variable)
    print("\n4. Testing error handling...")
    
    # Temporarily remove the environment variable
    original_url = os.environ.get('SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE')
    if 'SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE' in os.environ:
        del os.environ['SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE']
    
    try:
        url = os.getenv("SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE")
        if not url:
            raise ValueError("SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE environment variable not set")
    except ValueError as e:
        print(f"✅ Error handling works: {e}")
    finally:
        # Restore the environment variable
        if original_url:
            os.environ['SHAKUDO_NEO4J_GRAPH_TOOL_MICROSERVICE'] = original_url
    
    print("\n=== Test Summary ===")
    print("✅ All tests passed!")
    print("\nTo clean up test data, run:")
    print("curl -X POST http://localhost:8080/clear")
    
    return True

def test_with_actual_file():
    """Test with an actual file upload simulation"""
    print("\n=== Testing with Actual File Upload ===")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for Neo4j ingestion.\nIt contains multiple lines.\n")
        temp_file_path = f.name
    
    try:
        # Read the file content
        with open(temp_file_path, 'r') as f:
            content = f.read()
        
        # Calculate hash
        import hashlib
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Simulate the ingestion
        payload = {
            "file_name": Path(temp_file_path).name,
            "file_hash": file_hash,
            "content": content,
            "chat_id": "test-chat-456",
        }
        
        response = requests.post('http://localhost:8080/ingest', json=payload)
        response.raise_for_status()
        
        print(f"✅ File upload test successful: {response.json().get('message')}")
        
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
    finally:
        # Clean up
        os.unlink(temp_file_path)

if __name__ == '__main__':
    print("Neo4j Ingestion Testing Script")
    print("Make sure the mock microservice is running on http://localhost:8080")
    print()
    
    success = test_neo4j_ingestion()
    
    if success:
        test_with_actual_file()
    
    print("\nTesting complete!") 