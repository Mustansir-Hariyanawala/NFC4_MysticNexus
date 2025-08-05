# RAG Server with ChromaDB and LangGraph

A Flask-based REST API server for Retrieval-Augmented Generation (RAG) using ChromaDB for vector storage and LangGraph for workflow orchestration.

## Features

- **Document Processing**: Support for PDF, DOCX, and TXT files
- **Text Processing**: Advanced cleaning with spaCy, intelligent chunking with overlap
- **Vector Storage**: ChromaDB for persistent document embeddings
- **RAG Workflow**: LangGraph-based workflow for query processing
- **Comprehensive Logging**: Detailed logging of all workflow steps
- **API Endpoints**: RESTful APIs for document management and querying

## Project Structure

```
RAG_Server/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── config/
│   ├── __init__.py
│   └── chromaDB.py            # ChromaDB configuration and manager
├── routes/
│   ├── __init__.py
│   ├── main_router.py         # ChromaDB collection management APIs
│   └── rag_router.py          # RAG workflow APIs
├── utils/
│   ├── __init__.py
│   ├── doc_utils.py           # Document processing utilities
│   ├── logger_utils.py        # Logging configuration
│   ├── langgraph_workflow.py  # LangGraph RAG workflow
│   └── helpers.py             # Helper functions
└── logs/                      # Workflow execution logs
```

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install spaCy English model:**
```bash
python -m spacy download en_core_web_sm
```

3. **Create environment file (optional):**
```bash
# Create .env file for environment variables
GOOGLE_API_KEY=your_gemini_api_key_here
```

4. **Run the server:**
```bash
python app.py
```

The server will start on `http://localhost:5000` and automatically create the `./ChromaDB` directory.

## API Endpoints

### ChromaDB Collection Management

#### Create Collection
- **POST** `/api/create_collection`
- **Body**: 
```json
{
    "chatID": "unique_chat_identifier"
}
```

#### Delete Collection
- **DELETE** `/api/delete_collection`
- **Body**: 
```json
{
    "chatID": "unique_chat_identifier"
}
```

#### List Collections
- **GET** `/api/list_collections`

### RAG Workflow APIs

#### Process RAG (Complete Workflow)
- **POST** `/api/rag/process_rag`
- **Description**: Process documents and query through complete RAG pipeline
- **Body**: 
```json
{
    "queryText": "What is the main topic discussed?",
    "documents": [
        {
            "filename": "document.pdf",
            "content": "base64_encoded_file_content"
        }
    ],
    "chatID": "optional_chat_identifier"
}
```

#### Query Only (Existing Documents)
- **POST** `/api/rag/query_only`
- **Description**: Query against already processed documents
- **Body**: 
```json
{
    "queryText": "What is the main topic?",
    "chatID": "existing_chat_id"
}
```

#### Get RAG Status
- **GET** `/api/rag/rag_status/<chat_id>`
- **Description**: Check processing status for a chat ID

#### Get Processing Logs
- **GET** `/api/rag/get_logs/<chat_id>`
- **Description**: Retrieve detailed processing logs

### Health Check
- **GET** `/health`
- **Description**: Check server and service status

## LangGraph Workflow

The RAG workflow consists of the following nodes:

1. **Initialize** → Setup logging and state
2. **Clean Query** → Remove punctuation and stopwords from query
3. **Check Documents** → Validate document uploads and types
4. **Extract Text** → Extract text from PDF/DOCX/TXT files
5. **Clean Documents** → Clean extracted text using spaCy
6. **Chunk Documents** → Split text into overlapping chunks
7. **Embed Documents** → Generate embeddings for chunks
8. **Store in ChromaDB** → Store chunks with metadata
9. **Embed Query** → Generate query embedding
10. **Wait for Processing** → Ensure document processing completion
11. **Retrieve Documents** → Query ChromaDB for relevant chunks
12. **Generate Response** → Create final response using LLM

## Document Processing Features

### Original Functions (Mustansir's)
- `extract_text_from_file()` - Text extraction from various formats
- `clean_text_efficiently()` - spaCy-based text cleaning
- `chunk_text()` - Basic text chunking with overlap
- `generate_embeddings()` - Embedding generation

### Enhanced Functions (Sonnet Improvements)
- `_sonnet_clean_text_advanced()` - Enhanced text cleaning with normalization
- `_sonnet_chunk_text_intelligent()` - Smart boundary detection for chunking
- `_sonnet_generate_embeddings_batched()` - Batched embedding generation

## Logging and Debugging

All workflow executions are logged in detail:
- **Log Location**: `./logs/langgraph_{chat_id}_{timestamp}.txt`
- **Log Content**: Node execution, intermediate results, errors, statistics
- **Access**: Via API endpoint `/api/rag/get_logs/<chat_id>`

## Usage Examples

### 1. Complete RAG Processing
```bash
# Encode your document to base64
base64_content=$(base64 -w 0 document.pdf)

# Process with RAG
curl -X POST http://localhost:5000/api/rag/process_rag \
  -H "Content-Type: application/json" \
  -d '{
    "queryText": "What are the key findings?",
    "documents": [
      {
        "filename": "research.pdf",
        "content": "'$base64_content'"
      }
    ],
    "chatID": "research_session_1"
  }'
```

### 2. Query Existing Documents
```bash
curl -X POST http://localhost:5000/api/rag/query_only \
  -H "Content-Type: application/json" \
  -d '{
    "queryText": "Summarize the methodology",
    "chatID": "research_session_1"
  }'
```

### 3. Check Processing Status
```bash
curl -X GET http://localhost:5000/api/rag/rag_status/research_session_1
```

### 4. Get Processing Logs
```bash
curl -X GET http://localhost:5000/api/rag/get_logs/research_session_1
```

## Configuration

### ChromaDB Settings
- **Persistence Directory**: `./ChromaDB`
- **Collection Naming**: Based on chat IDs
- **Metadata Storage**: Chunk metadata, timestamps, file info

### Document Processing Settings
- **Max Chunk Size**: 1000 characters (configurable)
- **Overlap Size**: 200 characters (configurable)
- **Supported Formats**: PDF, DOCX, TXT
- **Embedding Model**: BAAI/bge-large-en-v1.5 (configurable)

### Text Processing
- **Query Cleaning**: Remove stopwords and punctuation
- **Document Cleaning**: Advanced normalization and spaCy processing
- **Chunking Strategy**: Intelligent boundary detection with sentence/paragraph breaks

## Error Handling

The system provides comprehensive error handling:
- **Validation Errors**: Invalid input format, missing fields
- **Processing Errors**: Document extraction, embedding generation failures
- **Storage Errors**: ChromaDB connection or storage issues
- **Workflow Errors**: Node execution failures with detailed logging

## Performance Considerations

- **Batched Embedding**: Process embeddings in configurable batches
- **Async Processing**: Non-blocking document processing
- **Memory Management**: Efficient handling of large documents
- **Logging**: Structured logging for debugging and monitoring

## Future Enhancements

- **LLM Integration**: Google AI Studio Gemini integration for response generation
- **Advanced Retrieval**: Hybrid search combining semantic and keyword search
- **Multi-modal Support**: Image and table extraction from PDFs
- **Caching**: Response caching for repeated queries
- **Authentication**: User management and access control
