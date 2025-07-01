#!/usr/bin/env python3
"""
Mock Neo4j Graph Tool Microservice for testing
Run this with: python mock_neo4j_microservice.py
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store ingested data in memory for testing
ingested_data = []

@app.route('/ingest', methods=['POST'])
def ingest_file():
    """Mock endpoint for file ingestion"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Validate required fields
        required_fields = ['file_name', 'file_hash', 'content', 'chat_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add timestamp
        data['ingested_at'] = datetime.now().isoformat()
        
        # Store the data
        ingested_data.append(data)
        
        logger.info(f"Successfully ingested file: {data['file_name']}")
        logger.info(f"Content length: {len(data['content'])} characters")
        logger.info(f"File hash: {data['file_hash']}")
        
        return jsonify({
            "status": "success",
            "message": f"File {data['file_name']} ingested successfully",
            "ingested_at": data['ingested_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing ingestion request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ingested', methods=['GET'])
def get_ingested_data():
    """Get all ingested data for verification"""
    return jsonify({
        "count": len(ingested_data),
        "data": ingested_data
    })

@app.route('/clear', methods=['POST'])
def clear_data():
    """Clear all ingested data"""
    global ingested_data
    ingested_data = []
    return jsonify({"message": "All data cleared"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    print("Starting Mock Neo4j Microservice on http://localhost:8081")
    print("Available endpoints:")
    print("  POST /ingest - Ingest a file")
    print("  GET  /ingested - Get all ingested data")
    print("  POST /clear - Clear all data")
    print("  GET  /health - Health check")
    print("\nTo test with curl:")
    print('curl -X POST http://localhost:8081/ingest \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"file_name": "test.txt", "file_hash": "abc123", "content": "test content", "chat_id": "123"}\'')
    
    app.run(host='0.0.0.0', port=8081, debug=True) 