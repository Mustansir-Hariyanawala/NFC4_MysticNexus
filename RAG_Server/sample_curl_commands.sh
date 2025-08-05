
# Sample cURL commands for testing RAG Server

# 1. Health Check
curl -X GET http://localhost:5000/health

# 2. Create Collection
curl -X POST http://localhost:5000/api/create_collection \
  -H "Content-Type: application/json" \
  -d '{"chatID": "tech_discussion_1"}'

# 3. Process RAG (with sample document)
curl -X POST http://localhost:5000/api/rag/process_rag \
  -H "Content-Type: application/json" \
  -d @sample_rag_request.json

# 4. Query Only
curl -X POST http://localhost:5000/api/rag/query_only \
  -H "Content-Type: application/json" \
  -d '{"queryText": "Tell me about quantum computing", "chatID": "tech_discussion_1"}'

# 5. Check RAG Status
curl -X GET http://localhost:5000/api/rag/rag_status/tech_discussion_1

# 6. Get Processing Logs
curl -X GET http://localhost:5000/api/rag/get_logs/tech_discussion_1

# 7. List Collections
curl -X GET http://localhost:5000/api/list_collections

# 8. Delete Collection
curl -X DELETE http://localhost:5000/api/delete_collection \
  -H "Content-Type: application/json" \
  -d '{"chatID": "tech_discussion_1"}'
