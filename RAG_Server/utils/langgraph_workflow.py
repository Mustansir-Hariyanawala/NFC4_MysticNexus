"""
LangGraph RAG Workflow Utility

This module defines the RAGWorkflow class, which orchestrates the Retrieval-Augmented Generation (RAG)
process using LangGraph. It handles document ingestion, cleaning, chunking, embedding, storage in ChromaDB,
query embedding, retrieval, and response generation.

Key Components:
    - RAGState: TypedDict defining the workflow state
    - RAGWorkflow: Main workflow class with node methods for each step
    - create_rag_workflow: Helper to instantiate the workflow

Usage:
    from utils.langgraph_workflow import create_rag_workflow
    workflow = create_rag_workflow()
    result = await workflow.run_workflow(query_text, documents, chat_id)
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.doc_utils import DocumentHandler, MustanDocumentManager
from utils.logger_utils import setup_langgraph_logger
from config.chromaDB import chroma_manager

# ---------------------------
# LangGraph Imports & Fallbacks
# ---------------------------
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from typing_extensions import TypedDict, Annotated
except ImportError:
    print("LangGraph not installed. Please install: pip install langgraph")
    # Dummy classes for development
    class StateGraph:
        def __init__(self): pass
        def add_node(self, name, func): pass
        def add_edge(self, start, end): pass
        def add_conditional_edges(self, start, condition, mapping): pass
        def compile(self): pass
    class END: pass
    def add_messages(x, y): return x + y
    class TypedDict: pass
    class Annotated: pass

# ---------------------------
# Workflow State Definition
# ---------------------------
class RAGState(TypedDict):
    # Input fields
    queryText: str
    documents: List[Dict[str, Any]]
    chat_id: str

    # Processing flags and intermediate states
    doc_processing_completed: bool
    query_cleaned: str
    extracted_texts: List[Dict[str, Any]]
    cleaned_documents: List[Dict[str, Any]]
    chunked_documents: List[Dict[str, Any]]
    chromadb_chunks: List[Dict[str, Any]]
    query_embedding: List[float]
    retrieved_docs: List[Dict[str, Any]]
    final_response: str

    # Error handling
    errors: List[str]

    # Logger
    logger: Any

# ---------------------------
# Main Workflow Class
# ---------------------------
class RAGWorkflow:
    """
    Orchestrates the RAG workflow using LangGraph.
    Each node represents a step in the pipeline.
    """
    def __init__(self, embedding_model: str = "BAAI/bge-large-en-v1.5"):
        self.doc_manager = MustanDocumentManager(model_name=embedding_model)
        self.doc_handler = DocumentHandler(self.doc_manager)
        self.workflow = None
        self._build_workflow()

    def _build_workflow(self):
        """Build the LangGraph workflow and define node transitions."""
        workflow = StateGraph(RAGState)
        # Add nodes
        workflow.add_node("initialize", self.initialize_node)
        workflow.add_node("clean_query", self.clean_query_node)
        workflow.add_node("check_documents", self.check_documents_node)
        workflow.add_node("extract_text", self.extract_text_node)
        workflow.add_node("clean_documents", self.clean_documents_node)
        workflow.add_node("chunk_documents", self.chunk_documents_node)
        workflow.add_node("embed_documents", self.embed_documents_node)
        workflow.add_node("store_in_chromadb", self.store_in_chromadb_node)
        workflow.add_node("embed_query", self.embed_query_node)
        workflow.add_node("wait_for_processing", self.wait_for_processing_node)
        workflow.add_node("retrieve_documents", self.retrieve_documents_node)
        workflow.add_node("generate_response", self.generate_response_node)
        # Define the flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "clean_query")
        workflow.add_edge("initialize", "check_documents")
        workflow.add_edge("check_documents", "extract_text")
        workflow.add_edge("extract_text", "clean_documents")
        workflow.add_edge("clean_documents", "chunk_documents")
        workflow.add_edge("chunk_documents", "embed_documents")
        workflow.add_edge("embed_documents", "store_in_chromadb")
        workflow.add_edge("clean_query", "embed_query")
        workflow.add_edge("embed_query", "wait_for_processing")
        workflow.add_edge("store_in_chromadb", "wait_for_processing")
        workflow.add_edge("wait_for_processing", "retrieve_documents")
        workflow.add_edge("retrieve_documents", "generate_response")
        workflow.add_edge("generate_response", END)
        self.workflow = workflow.compile()

    # ---------------------------
    # Workflow Node Methods
    # ---------------------------

    async def initialize_node(self, state: RAGState) -> RAGState:
        """Initialize workflow state and logger."""
        chat_id = state.get("chat_id", f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger = setup_langgraph_logger(chat_id)
        logger.log_node_start("initialize", {
            "chat_id": chat_id,
            "query_length": len(state.get("queryText", "")),
            "documents_count": len(state.get("documents", []))
        })
        new_state = {
            **state,
            "chat_id": chat_id,
            "doc_processing_completed": False,
            "errors": [],
            "logger": logger
        }
        logger.log_node_end("initialize", {"status": "initialized"})
        return new_state

    async def clean_query_node(self, state: RAGState) -> RAGState:
        """Clean the query text by removing punctuation and stopwords."""
        logger = state["logger"]
        logger.log_node_start("clean_query", {"original_query": state["queryText"]})
        try:
            query_text = state["queryText"]
            if hasattr(self.doc_manager, '_sonnet_clean_text_advanced'):
                cleaned_query = await self.doc_manager._sonnet_clean_text_advanced(query_text)
            else:
                cleaned_query = await self.doc_manager.clean_text(query_text)
            logger.log_intermediate_result("query_cleaning", {
                "original": query_text,
                "cleaned": cleaned_query
            }, "Query cleaned successfully")
            new_state = {**state, "query_cleaned": cleaned_query}
            logger.log_node_end("clean_query", {"cleaned_query": cleaned_query})
            return new_state
        except Exception as e:
            logger.log_error("clean_query", e)
            errors = state.get("errors", [])
            errors.append(f"Query cleaning error: {str(e)}")
            return {**state, "errors": errors, "query_cleaned": state["queryText"]}

    async def check_documents_node(self, state: RAGState) -> RAGState:
        """Check if documents are uploaded and determine processing path."""
        logger = state["logger"]
        logger.log_node_start("check_documents", {
            "documents_count": len(state.get("documents", []))
        })
        try:
            documents = state.get("documents", [])
            if not documents:
                logger.log_intermediate_result("document_check", {
                    "status": "no_documents",
                    "action": "skip_processing"
                }, "No documents to process, setting processing as completed")
                new_state = {**state, "doc_processing_completed": True}
                logger.log_node_end("check_documents", {"status": "no_documents_completed"})
                return new_state
            doc_types = []
            supported_docs = []
            for doc in documents:
                filename = doc.get("filename", "unknown")
                doc_type = await self.doc_handler.check_document_type(filename)
                doc_types.append({"filename": filename, "type": doc_type})
                if doc_type != "unsupported":
                    supported_docs.append(doc)
            logger.log_intermediate_result("document_types", doc_types,
                                         f"Found {len(supported_docs)} supported documents")
            new_state = {
                **state,
                "documents": supported_docs,
                "doc_processing_completed": len(supported_docs) == 0
            }
            logger.log_node_end("check_documents", {
                "supported_count": len(supported_docs),
                "processing_needed": len(supported_docs) > 0
            })
            return new_state
        except Exception as e:
            logger.log_error("check_documents", e)
            errors = state.get("errors", [])
            errors.append(f"Document checking error: {str(e)}")
            return {**state, "errors": errors, "doc_processing_completed": True}

    async def extract_text_node(self, state: RAGState) -> RAGState:
        """Extract text from documents based on their type."""
        logger = state["logger"]
        logger.log_node_start("extract_text", {
            "documents_to_process": len(state.get("documents", []))
        })
        try:
            documents = state.get("documents", [])
            extracted_texts = []
            for i, doc in enumerate(documents):
                try:
                    filename = doc.get("filename", f"doc_{i}")
                    content = doc.get("content", b"")
                    if not content:
                        logger.log_intermediate_result("text_extraction", {
                            "filename": filename,
                            "status": "no_content"
                        }, "Skipping document with no content")
                        continue
                    extracted_text = await self.doc_manager.extract_text_from_file(content, filename)
                    extracted_doc = {
                        "filename": filename,
                        "original_text": extracted_text,
                        "text_length": len(extracted_text),
                        "word_count": len(extracted_text.split())
                    }
                    extracted_texts.append(extracted_doc)
                    logger.log_intermediate_result("text_extraction", {
                        "filename": filename,
                        "text_length": len(extracted_text),
                        "word_count": len(extracted_text.split())
                    }, f"Successfully extracted text from {filename}")
                except Exception as e:
                    logger.log_error("extract_text", e, f"Failed to extract from {doc.get('filename', 'unknown')}")
                    continue
            new_state = {**state, "extracted_texts": extracted_texts}
            logger.log_node_end("extract_text", {
                "extracted_count": len(extracted_texts),
                "total_words": sum(doc["word_count"] for doc in extracted_texts)
            })
            return new_state
        except Exception as e:
            logger.log_error("extract_text", e)
            errors = state.get("errors", [])
            errors.append(f"Text extraction error: {str(e)}")
            return {**state, "errors": errors, "extracted_texts": []}

    async def clean_documents_node(self, state: RAGState) -> RAGState:
        """Clean extracted text from documents."""
        logger = state["logger"]
        extracted_texts = state.get("extracted_texts", [])
        logger.log_node_start("clean_documents", {
            "documents_to_clean": len(extracted_texts)
        })
        try:
            cleaned_documents = []
            for doc in extracted_texts:
                try:
                    original_text = doc["original_text"]
                    if hasattr(self.doc_manager, '_sonnet_clean_text_advanced'):
                        cleaned_text = await self.doc_manager._sonnet_clean_text_advanced(original_text)
                    else:
                        cleaned_text = await self.doc_manager.clean_text(original_text)
                    cleaned_doc = {
                        **doc,
                        "cleaned_text": cleaned_text,
                        "cleaned_length": len(cleaned_text),
                        "cleaned_word_count": len(cleaned_text.split())
                    }
                    cleaned_documents.append(cleaned_doc)
                    logger.log_intermediate_result("text_cleaning", {
                        "filename": doc["filename"],
                        "original_length": len(original_text),
                        "cleaned_length": len(cleaned_text),
                        "reduction_ratio": 1 - (len(cleaned_text) / len(original_text)) if len(original_text) > 0 else 0
                    }, f"Cleaned text for {doc['filename']}")
                except Exception as e:
                    logger.log_error("clean_documents", e, f"Failed to clean {doc.get('filename', 'unknown')}")
                    continue
            new_state = {**state, "cleaned_documents": cleaned_documents}
            logger.log_node_end("clean_documents", {
                "cleaned_count": len(cleaned_documents),
                "total_cleaned_words": sum(doc["cleaned_word_count"] for doc in cleaned_documents)
            })
            return new_state
        except Exception as e:
            logger.log_error("clean_documents", e)
            errors = state.get("errors", [])
            errors.append(f"Document cleaning error: {str(e)}")
            return {**state, "errors": errors, "cleaned_documents": []}

    async def chunk_documents_node(self, state: RAGState) -> RAGState:
        """Chunk cleaned documents with overlap."""
        logger = state["logger"]
        cleaned_documents = state.get("cleaned_documents", [])
        logger.log_node_start("chunk_documents", {
            "documents_to_chunk": len(cleaned_documents)
        })
        try:
            chunked_documents = []
            total_chunks = 0
            for doc in cleaned_documents:
                try:
                    cleaned_text = doc["cleaned_text"]
                    if hasattr(self.doc_manager, '_sonnet_chunk_text_intelligent'):
                        chunks = await self.doc_manager._sonnet_chunk_text_intelligent(
                            cleaned_text, max_chunk_size=1000, overlap_size=200
                        )
                    else:
                        chunks = await self.doc_manager.chunk_text(
                            cleaned_text, max_chunk_size=1000, overlap_size=200
                        )
                    chunked_doc = {
                        **doc,
                        "chunks": chunks,
                        "chunk_count": len(chunks)
                    }
                    chunked_documents.append(chunked_doc)
                    total_chunks += len(chunks)
                    logger.log_intermediate_result("text_chunking", {
                        "filename": doc["filename"],
                        "text_length": len(cleaned_text),
                        "chunk_count": len(chunks),
                        "avg_chunk_size": sum(len(chunk["text"]) for chunk in chunks) // len(chunks) if chunks else 0
                    }, f"Chunked {doc['filename']} into {len(chunks)} chunks")
                except Exception as e:
                    logger.log_error("chunk_documents", e, f"Failed to chunk {doc.get('filename', 'unknown')}")
                    continue
            new_state = {**state, "chunked_documents": chunked_documents}
            logger.log_node_end("chunk_documents", {
                "documents_chunked": len(chunked_documents),
                "total_chunks": total_chunks
            })
            return new_state
        except Exception as e:
            logger.log_error("chunk_documents", e)
            errors = state.get("errors", [])
            errors.append(f"Document chunking error: {str(e)}")
            return {**state, "errors": errors, "chunked_documents": []}

    async def embed_documents_node(self, state: RAGState) -> RAGState:
        """Generate embeddings for document chunks."""
        logger = state["logger"]
        chunked_documents = state.get("chunked_documents", [])
        logger.log_node_start("embed_documents", {
            "documents_with_chunks": len(chunked_documents)
        })
        try:
            all_chunks = []
            chunk_texts = []
            for doc in chunked_documents:
                for chunk in doc["chunks"]:
                    all_chunks.append({
                        "doc_filename": doc["filename"],
                        "chunk_data": chunk,
                        "original_text": doc["original_text"]
                    })
                    chunk_texts.append(chunk["text"])
            logger.log_intermediate_result("embedding_preparation", {
                "total_chunks": len(all_chunks),
                "total_text_length": sum(len(text) for text in chunk_texts)
            }, "Prepared chunks for embedding")
            if hasattr(self.doc_manager, '_sonnet_generate_embeddings_batched'):
                embeddings = await self.doc_manager._sonnet_generate_embeddings_batched(chunk_texts)
            else:
                embeddings = await self.doc_manager.generate_embeddings(chunk_texts)
            embedded_chunks = []
            for i, chunk_info in enumerate(all_chunks):
                embedded_chunk = {
                    **chunk_info,
                    "embedding": embeddings[i]
                }
                embedded_chunks.append(embedded_chunk)
            new_state = {**state, "embedded_chunks": embedded_chunks}
            logger.log_node_end("embed_documents", {
                "embedded_chunks": len(embedded_chunks),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0
            })
            return new_state
        except Exception as e:
            logger.log_error("embed_documents", e)
            errors = state.get("errors", [])
            errors.append(f"Document embedding error: {str(e)}")
            return {**state, "errors": errors, "embedded_chunks": []}

    async def store_in_chromadb_node(self, state: RAGState) -> RAGState:
        """Store processed chunks in ChromaDB."""
        logger = state["logger"]
        embedded_chunks = state.get("embedded_chunks", [])
        chat_id = state["chat_id"]
        logger.log_node_start("store_in_chromadb", {
            "chunks_to_store": len(embedded_chunks),
            "chat_id": chat_id
        })
        try:
            collection_result = chroma_manager.create_collection(chat_id)
            logger.log_intermediate_result("collection_creation", collection_result,
                                         "Ensured ChromaDB collection exists")
            collection = chroma_manager.get_collection(chat_id)
            if not collection:
                raise Exception(f"Failed to get collection for chat_id: {chat_id}")
            chunk_ids = []
            embeddings_list = []
            metadatas = []
            documents = []
            for i, chunk_info in enumerate(embedded_chunks):
                chunk_data = chunk_info["chunk_data"]
                chunk_id = self.doc_handler.generate_chunk_id(
                    chat_id, i, chunk_info["doc_filename"]
                )
                metadata = {
                    "filename": chunk_info["doc_filename"],
                    "chunk_index": chunk_data.get("chunk_index", i),
                    "total_chunks": chunk_data.get("total_chunks", len(embedded_chunks)),
                    "start_pos": chunk_data.get("start_pos", 0),
                    "end_pos": chunk_data.get("end_pos", 0),
                    "token_count": chunk_data.get("token_count", len(chunk_data["text"].split())),
                    "chat_id": chat_id,
                    "created_at": datetime.now().isoformat()
                }
                start_pos = chunk_data.get("start_pos", 0)
                end_pos = chunk_data.get("end_pos", len(chunk_info["original_text"]))
                original_chunk_text = chunk_info["original_text"][start_pos:end_pos]
                chunk_ids.append(chunk_id)
                embeddings_list.append(chunk_info["embedding"])
                metadatas.append(metadata)
                documents.append(original_chunk_text)
            collection.add(
                ids=chunk_ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents
            )
            logger.log_intermediate_result("chromadb_storage", {
                "stored_chunks": len(chunk_ids),
                "collection_name": chat_id
            }, "Successfully stored chunks in ChromaDB")
            new_state = {
                **state,
                "doc_processing_completed": True,
                "chromadb_chunks": embedded_chunks
            }
            logger.log_node_end("store_in_chromadb", {
                "status": "completed",
                "stored_chunks": len(chunk_ids)
            })
            return new_state
        except Exception as e:
            logger.log_error("store_in_chromadb", e)
            errors = state.get("errors", [])
            errors.append(f"ChromaDB storage error: {str(e)}")
            return {**state, "errors": errors, "doc_processing_completed": True}

    async def embed_query_node(self, state: RAGState) -> RAGState:
        """Generate embedding for the cleaned query."""
        logger = state["logger"]
        query_cleaned = state.get("query_cleaned", state.get("queryText", ""))
        logger.log_node_start("embed_query", {"query": query_cleaned})
        try:
            query_embeddings = await self.doc_manager.generate_embeddings([query_cleaned])
            query_embedding = query_embeddings[0]
            logger.log_intermediate_result("query_embedding", {
                "query": query_cleaned,
                "embedding_dimension": len(query_embedding)
            }, "Generated query embedding")
            new_state = {**state, "query_embedding": query_embedding}
            logger.log_node_end("embed_query", {
                "embedding_dimension": len(query_embedding)
            })
            return new_state
        except Exception as e:
            logger.log_error("embed_query", e)
            errors = state.get("errors", [])
            errors.append(f"Query embedding error: {str(e)}")
            return {**state, "errors": errors, "query_embedding": []}

    async def wait_for_processing_node(self, state: RAGState) -> RAGState:
        """Wait for document processing to complete."""
        logger = state["logger"]
        logger.log_node_start("wait_for_processing", {
            "doc_processing_completed": state.get("doc_processing_completed", False)
        })
        processing_completed = state.get("doc_processing_completed", False)
        logger.log_intermediate_result("processing_check", {
            "completed": processing_completed
        }, "Checked document processing status")
        logger.log_node_end("wait_for_processing", {
            "status": "ready" if processing_completed else "waiting"
        })
        return state

    async def retrieve_documents_node(self, state: RAGState) -> RAGState:
        """Retrieve relevant documents from ChromaDB using query embedding."""
        logger = state["logger"]
        query_embedding = state.get("query_embedding", [])
        chat_id = state["chat_id"]
        logger.log_node_start("retrieve_documents", {
            "chat_id": chat_id,
            "query_embedding_ready": len(query_embedding) > 0
        })
        try:
            if not query_embedding:
                raise Exception("No query embedding available")
            collection = chroma_manager.get_collection(chat_id)
            if not collection:
                logger.log_intermediate_result("retrieval", {
                    "status": "no_collection"
                }, "No collection found, returning empty results")
                return {**state, "retrieved_docs": []}
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, doc_text in enumerate(results["documents"][0]):
                    retrieved_doc = {
                        "document_text": doc_text,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    }
                    retrieved_docs.append(retrieved_doc)
            logger.log_intermediate_result("document_retrieval", {
                "retrieved_count": len(retrieved_docs),
                "distances": [doc["distance"] for doc in retrieved_docs]
            }, "Retrieved relevant documents from ChromaDB")
            new_state = {**state, "retrieved_docs": retrieved_docs}
            logger.log_node_end("retrieve_documents", {
                "retrieved_count": len(retrieved_docs)
            })
            return new_state
        except Exception as e:
            logger.log_error("retrieve_documents", e)
            errors = state.get("errors", [])
            errors.append(f"Document retrieval error: {str(e)}")
            return {**state, "errors": errors, "retrieved_docs": []}

    async def generate_response_node(self, state: RAGState) -> RAGState:
        """Generate final response using LLM with query and retrieved documents."""
        logger = state["logger"]
        query_text = state.get("queryText", "")
        retrieved_docs = state.get("retrieved_docs", [])
        logger.log_node_start("generate_response", {
            "query": query_text,
            "retrieved_docs_count": len(retrieved_docs)
        })
        try:
            context_parts = []
            for i, doc in enumerate(retrieved_docs):
                context_parts.append(f"Document {i+1}:\n{doc['document_text']}\n")
            context = "\n".join(context_parts)
            if retrieved_docs:
                response = f"""Based on the provided documents, here's the response to your query: "{query_text}"

Retrieved Context:
{context}

This is a placeholder response. In a full implementation, this would be generated by Google AI Studio Gemini or another LLM using the query and context above."""
            else:
                response = f"""I couldn't find relevant documents to answer your query: "{query_text}"

This might be because:
1. No documents were provided
2. The documents don't contain relevant information
3. There was an error in processing

Please try providing more relevant documents or rephrasing your query."""
            logger.log_intermediate_result("response_generation", {
                "query": query_text,
                "context_length": len(context),
                "response_length": len(response)
            }, "Generated final response")
            logger.log_processing_stats({
                "Total Documents Processed": len(state.get("documents", [])),
                "Total Chunks Created": len(state.get("chromadb_chunks", [])),
                "Retrieved Documents": len(retrieved_docs),
                "Errors Encountered": len(state.get("errors", [])),
                "Processing Completed": state.get("doc_processing_completed", False)
            })
            new_state = {**state, "final_response": response}
            logger.log_node_end("generate_response", {
                "response_length": len(response),
                "status": "completed"
            })
            logger.close()
            return new_state
        except Exception as e:
            logger.log_error("generate_response", e)
            errors = state.get("errors", [])
            errors.append(f"Response generation error: {str(e)}")
            error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            return {**state, "errors": errors, "final_response": error_response}

    # ---------------------------
    # Workflow Runner
    # ---------------------------
    async def run_workflow(self, query_text: str, documents: List[Dict[str, Any]],
                          chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete RAG workflow.

        Args:
            query_text (str): The user's query.
            documents (List[Dict]): List of uploaded documents.
            chat_id (str, optional): Unique chat/session ID.

        Returns:
            Dict[str, Any]: Workflow results including response, errors, stats.
        """
        if not chat_id:
            chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        initial_state = {
            "queryText": query_text,
            "documents": documents,
            "chat_id": chat_id
        }
        final_state = await self.workflow.ainvoke(initial_state)
        return {
            "chat_id": chat_id,
            "query": query_text,
            "response": final_state.get("final_response", "No response generated"),
            "errors": final_state.get("errors", []),
            "doc_processing_completed": final_state.get("doc_processing_completed", False),
            "retrieved_docs_count": len(final_state.get("retrieved_docs", [])),
            "total_chunks_processed": len(final_state.get("chromadb_chunks", []))
        }

# ---------------------------
# Workflow Factory
# ---------------------------
def create_rag_workflow(embedding_model: str = "BAAI/bge-large-en-v1.5") -> RAGWorkflow:
    """
    Create and return a RAG workflow instance.

    Args:
        embedding_model (str): Embedding model name.

    Returns:
        RAGWorkflow: Initialized workflow object.
    """
    return RAGWorkflow(embedding_model=embedding_model)