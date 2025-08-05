import asyncio
import requests
import json
from typing import Dict, List, Optional, Any, TypedDict
from langgraph.graph import StateGraph, END
from datetime import datetime
import logging

from config.chromadb import add_document_to_chat, query_chat_documents, get_chat_collection
from utils.document_manager import DocumentManager

logger = logging.getLogger(__name__)

class RAGState(TypedDict):
    """State for the RAG workflow"""
    chat_id: str
    user_id: str
    query: str
    document: Optional[Dict[str, Any]]  # File data if uploaded
    document_chunks: List[str]  # Processed document chunks
    query_embedding: List[float]  # Query embeddings
    retrieved_docs: List[Dict]  # Retrieved relevant documents
    context: str  # Formatted context for LLM
    response: str  # Final LLM response
    citations: List[str]  # Document citations
    doc_chunk_ids: List[str]  # IDs of stored document chunks
    error: Optional[str]
    processing_status: str

class LocalOllamaLLM:
    """Local Ollama LLM client running on same machine"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama2:7b-chat"):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = 120  # 2 minutes timeout
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using local Ollama"""
        try:
            # Construct the full prompt
            if context.strip():
                full_prompt = f"""You are a helpful AI assistant. Use the provided context to answer the user's question accurately and comprehensively.

Context:
{context}

Question: {prompt}

Answer: Based on the context provided above, """
            else:
                full_prompt = f"""You are a helpful AI assistant. Answer the following question:

{prompt}

Answer: """
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            }
            
            # Use synchronous requests since we're on the same machine
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "Sorry, I couldn't generate a response.")
                logger.info(f"Generated response from local Ollama: {len(generated_text)} characters")
                return generated_text
            else:
                logger.error(f"Ollama API error {response.status_code}: {response.text}")
                return f"Error: Local LLM server returned status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to local Ollama server")
            return "Error: Could not connect to the local AI server. Please make sure Ollama is running with: 'ollama serve'"
        except requests.exceptions.Timeout:
            logger.error("Timeout connecting to local Ollama server")
            return "Error: Request timed out. The AI model might be loading or busy."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"

class RAGWorkflow:
    def __init__(self, model_name: str = "llama2:7b-chat", ollama_url: str = "http://localhost:11434"):
        """Initialize RAG workflow with local Ollama"""
        self.document_manager = DocumentManager()
        self.llm = LocalOllamaLLM(base_url=ollama_url, model_name=model_name)
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(RAGState)
        
        # Add nodes
        workflow.add_node("check_document", self._check_document_node)
        workflow.add_node("process_document", self._process_document_node)
        workflow.add_node("embed_query", self._embed_query_node)
        workflow.add_node("wait_for_processing", self._wait_for_processing_node)
        workflow.add_node("retrieve_documents", self._retrieve_documents_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("check_document")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "check_document",
            self._should_process_document,
            {
                "process": "process_document",
                "skip": "embed_query",
                "error": "handle_error"
            }
        )
        
        # Workflow edges (parallel processing happens here)
        workflow.add_edge("process_document", "embed_query")
        workflow.add_edge("embed_query", "wait_for_processing")
        workflow.add_edge("wait_for_processing", "retrieve_documents")
        workflow.add_edge("retrieve_documents", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()

    def _should_process_document(self, state: RAGState) -> str:
        """Decide workflow path based on document presence and errors"""
        if state.get("error"):
            return "error"
        return "process" if state.get("document") else "skip"

    async def _check_document_node(self, state: RAGState) -> RAGState:
        """Validate document if present"""
        try:
            if state.get("document"):
                document = state["document"]
                if not document.get("content") or not document.get("filename"):
                    state["error"] = "Invalid document format"
                    return state
                
                # Validate file type
                filename = document["filename"]
                if not self.document_manager._is_supported_format(filename):
                    state["error"] = f"Unsupported file format: {filename}"
                    return state
                    
                state["processing_status"] = "document_validated"
                logger.info(f"Document validated: {filename}")
            else:
                state["processing_status"] = "no_document"
                logger.info("No document to process")
                
            return state
            
        except Exception as e:
            state["error"] = f"Document validation error: {str(e)}"
            logger.error(f"Document validation failed: {e}")
            return state

    async def _process_document_node(self, state: RAGState) -> RAGState:
        """Process document and store in ChromaDB (runs in parallel with query embedding)"""
        try:
            document = state["document"]
            chat_id = state["chat_id"]
            
            logger.info(f"Processing document: {document['filename']}")
            
            # Extract text from document
            extracted_text = await self.document_manager.extract_text_from_file(
                document["content"], 
                document["filename"]
            )
            
            # Clean and chunk the text
            cleaned_text = self.document_manager.clean_text(extracted_text)
            chunks = self.document_manager.chunk_text(cleaned_text)
            
            logger.info(f"Document processed into {len(chunks)} chunks")
            
            # Generate embeddings and store each chunk
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_embedding = await self.document_manager.generate_embeddings(chunk)
                
                # Store in ChromaDB
                chunk_id = await add_document_to_chat(
                    chat_id=chat_id,
                    doc_text=extracted_text,
                    cleaned_text=chunk,
                    embeddings=chunk_embedding,
                    metadata={
                        "filename": document["filename"],
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "uploaded_at": datetime.utcnow().isoformat()
                    }
                )
                chunk_ids.append(chunk_id)
            
            state["document_chunks"] = chunks
            state["doc_chunk_ids"] = chunk_ids
            state["processing_status"] = "document_processed"
            
            logger.info(f"Document stored in ChromaDB with {len(chunk_ids)} chunks")
            return state
            
        except Exception as e:
            state["error"] = f"Document processing error: {str(e)}"
            logger.error(f"Document processing failed: {e}")
            return state

    async def _embed_query_node(self, state: RAGState) -> RAGState:
        """Generate embeddings for the user query (runs in parallel with document processing)"""
        try:
            query = state["query"]
            logger.info(f"Generating embeddings for query: {query[:50]}...")
            
            query_embedding = await self.document_manager.generate_embeddings(query)
            state["query_embedding"] = query_embedding
            state["processing_status"] = "query_embedded"
            
            logger.info("Query embeddings generated successfully")
            return state
            
        except Exception as e:
            state["error"] = f"Query embedding error: {str(e)}"
            logger.error(f"Query embedding failed: {e}")
            return state

    async def _wait_for_processing_node(self, state: RAGState) -> RAGState:
        """Synchronization point - wait for both document processing and query embedding"""
        try:
            # Small delay to ensure any async operations complete
            await asyncio.sleep(0.1)
            
            state["processing_status"] = "ready_for_retrieval"
            logger.info("Ready for document retrieval")
            return state
            
        except Exception as e:
            state["error"] = f"Processing synchronization error: {str(e)}"
            return state

    async def _retrieve_documents_node(self, state: RAGState) -> RAGState:
        """Retrieve relevant documents from ChromaDB"""
        try:
            chat_id = state["chat_id"]
            query_embedding = state["query_embedding"]
            
            logger.info(f"Retrieving relevant documents for chat {chat_id}")
            
            # Check if collection exists
            collection = await get_chat_collection(chat_id)
            if not collection:
                logger.info("No document collection found for this chat")
                state["retrieved_docs"] = []
                state["context"] = ""
                state["citations"] = []
                return state
            
            # Query ChromaDB for relevant documents
            results = await query_chat_documents(
                chat_id=chat_id,
                query_embeddings=query_embedding,
                n_results=5
            )
            
            # Format retrieved documents
            retrieved_docs = []
            citations = []
            
            if results and results.get("documents"):
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    similarity_score = 1 - distance
                    
                    # Only include documents with reasonable similarity
                    if similarity_score > 0.3:
                        retrieved_docs.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity_score": similarity_score
                        })
                        
                        # Create citation
                        filename = metadata.get("filename", "Unknown")
                        chunk_idx = metadata.get("chunk_index", 0)
                        citations.append(f"{filename} (section {chunk_idx + 1})")
            
            # Format context for LLM (use top 3 most relevant chunks)
            if retrieved_docs:
                context_parts = []
                for i, doc in enumerate(retrieved_docs[:3]):
                    context_parts.append(f"[Document {i+1}]: {doc['content']}")
                context = "\n\n".join(context_parts)
            else:
                context = ""
            
            state["retrieved_docs"] = retrieved_docs
            state["context"] = context
            state["citations"] = citations
            state["processing_status"] = "documents_retrieved"
            
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            return state
            
        except Exception as e:
            state["error"] = f"Document retrieval error: {str(e)}"
            logger.error(f"Document retrieval failed: {e}")
            return state

    async def _generate_response_node(self, state: RAGState) -> RAGState:
        """Generate response using local Ollama LLM"""
        try:
            query = state["query"]
            context = state["context"]
            
            logger.info("Generating response using local Ollama LLM")
            
            # Generate response using local Ollama
            response = await asyncio.to_thread(self.llm.generate_response, query, context)
            
            state["response"] = response
            state["processing_status"] = "completed"
            
            logger.info(f"Response generated successfully: {len(response)} characters")
            return state
            
        except Exception as e:
            state["error"] = f"Response generation error: {str(e)}"
            logger.error(f"Response generation failed: {e}")
            return state

    async def _handle_error_node(self, state: RAGState) -> RAGState:
        """Handle errors in the workflow"""
        error = state.get("error", "Unknown error occurred")
        state["response"] = f"I apologize, but I encountered an error: {error}"
        state["processing_status"] = "error"
        logger.error(f"Workflow error: {error}")
        return state

    async def process_rag_request(
        self, 
        chat_id: str, 
        user_id: str, 
        query: str, 
        document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a complete RAG request through the workflow"""
        
        logger.info(f"Starting RAG request for chat {chat_id}, user {user_id}")
        
        initial_state = RAGState(
            chat_id=chat_id,
            user_id=user_id,
            query=query,
            document=document,
            document_chunks=[],
            query_embedding=[],
            retrieved_docs=[],
            context="",
            response="",
            citations=[],
            doc_chunk_ids=[],
            error=None,
            processing_status="initialized"
        )
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            result = {
                "response": final_state["response"],
                "citations": final_state.get("citations", []),
                "doc_chunk_ids": final_state.get("doc_chunk_ids", []),
                "status": final_state["processing_status"],
                "error": final_state.get("error")
            }
            
            logger.info(f"RAG request completed with status: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"RAG workflow failed: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "citations": [],
                "doc_chunk_ids": [],
                "status": "error",
                "error": str(e)
            }
