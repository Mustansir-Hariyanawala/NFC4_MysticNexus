"""
Document Utilities for RAG Workflow

This module provides classes and functions for document ingestion, cleaning, chunking, and embedding.
It supports PDF, DOCX, and TXT formats, and integrates with spaCy and HuggingFace for NLP and embeddings.

Key Components:
    - MustanDocumentManager: Main class for document processing
    - DocumentHandler: Helper for chunk IDs and ChromaDB preparation
    - Standalone async functions for extraction, cleaning, chunking, and embedding

Usage:
    manager = MustanDocumentManager()
    cleaned = await manager.clean_text(text)
    chunks = await manager.chunk_text(text)
    embeddings = await manager.generate_embeddings([text])
"""

import os
import io
import re
import tempfile
import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

# ---------------------------
# Third-party Imports & spaCy Model
# ---------------------------
try:
    import spacy
    from langchain_community.document_loaders import PyMuPDFLoader
    from langchain_huggingface import HuggingFaceEmbeddings
    from docx import Document
    import PyPDF2
except ImportError as e:
    print(f"Required package not installed: {e}")
    print("Please install: pip install spacy langchain-community langchain-huggingface python-docx PyPDF2")

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Please install spacy English model: python -m spacy download en_core_web_sm")
    nlp = None

logger = logging.getLogger(__name__)

# ---------------------------
# MustanDocumentManager Class
# ---------------------------
class MustanDocumentManager:
    """
    Handles document extraction, cleaning, chunking, and embedding.
    """
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.nlp_model = nlp
        self.supported_formats = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }

    def _is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported."""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.supported_formats

    async def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """
        Extract text from uploaded file (PDF, DOCX, TXT).
        Uses PyMuPDFLoader for PDFs, python-docx for DOCX, and utf-8 decode for TXT.
        """
        try:
            ext = os.path.splitext(filename.lower())[1]
            if ext == '.pdf':
                return await self._extract_from_pdf_mustan(file_content, filename)
            elif ext == '.docx':
                return await self._extract_from_docx(file_content)
            elif ext == '.txt':
                return file_content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise

    async def _extract_from_pdf_mustan(self, file_content: bytes, filename: str) -> str:
        """
        Extract text from PDF using PyMuPDFLoader.
        Falls back to PyPDF2 if needed.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            try:
                loader = PyMuPDFLoader(temp_file_path)
                documents = loader.load()
                text = ""
                for doc in documents:
                    text += doc.page_content + "\n"
                return text.strip()
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        except Exception as e:
            logger.error(f"Error extracting PDF text with PyMuPDF: {e}")
            return await self._extract_from_pdf_fallback(file_content)

    async def _extract_from_pdf_fallback(self, file_content: bytes) -> str:
        """
        Fallback PDF extraction using PyPDF2.
        """
        try:
            text = ""
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error with fallback PDF extraction: {e}")
            raise

    async def _extract_from_docx(self, file_content: bytes) -> str:
        """
        Extract text from DOCX file.
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise

    def document_object_to_text(self, documents) -> List[str]:
        """
        Convert document objects to text list.
        """
        return [doc.page_content for doc in documents]

    def clean_text_efficiently(self, texts: List[str]) -> List[str]:
        """
        Clean text efficiently using spaCy.
        Removes stopwords and punctuation.
        """
        if not self.nlp_model:
            logger.warning("spaCy model not loaded, using basic cleaning")
            return [self._basic_clean_text(text) for text in texts]
        try:
            processed_texts = []
            for doc in self.nlp_model.pipe(texts):
                filtered_text = " ".join(
                    token.text for token in doc if not token.is_stop and not token.is_punct
                )
                processed_texts.append(filtered_text)
            return processed_texts
        except Exception as e:
            logger.error(f"Error in spaCy text cleaning: {e}")
            return [self._basic_clean_text(text) for text in texts]

    def _basic_clean_text(self, text: str) -> str:
        """
        Basic text cleaning fallback.
        """
        try:
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n+', '\n', text)
            text = text.strip()
            if len(text) < 50:
                return text
            return text
        except Exception as e:
            logger.error(f"Error in basic cleaning: {e}")
            return text

    async def clean_text(self, text: str) -> str:
        """
        Clean single text (wrapper for efficient cleaning).
        """
        try:
            cleaned_texts = self.clean_text_efficiently([text])
            return cleaned_texts[0] if cleaned_texts else text
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text

    async def chunk_text(self, text: str, max_chunk_size: int = 1000, overlap_size: int = 200) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks with metadata.
        Attempts to split at sentence boundaries.
        """
        try:
            if len(text) <= max_chunk_size:
                return [{
                    "text": text,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "start_pos": 0,
                    "end_pos": len(text)
                }]
            chunks = []
            start = 0
            chunk_index = 0
            while start < len(text):
                end = start + max_chunk_size
                if end < len(text):
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end > start + max_chunk_size // 2:
                        end = sentence_end + 1
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "chunk_index": chunk_index,
                        "total_chunks": 0,
                        "start_pos": start,
                        "end_pos": end
                    })
                    chunk_index += 1
                start = end - overlap_size
                if start >= len(text):
                    break
            total_chunks = len(chunks)
            for chunk in chunks:
                chunk["total_chunks"] = total_chunks
            return chunks
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            return [{
                "text": text,
                "chunk_index": 0,
                "total_chunks": 1,
                "start_pos": 0,
                "end_pos": len(text)
            }]

    def embedding_text(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text list using HuggingFace.
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Async wrapper for embedding generation.
        """
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self.embedding_text, texts
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    async def process_document_complete(self, file_content: bytes, filename: str, 
                                      max_chunk_size: int = 1000, overlap_size: int = 200) -> Dict[str, Any]:
        """
        Complete document processing pipeline: extract, clean, chunk, embed.
        """
        try:
            logger.info(f"Extracting text from {filename}")
            text = await self.extract_text_from_file(file_content, filename)
            logger.info(f"Cleaning text from {filename}")
            cleaned_text = await self.clean_text(text)
            logger.info(f"Chunking text from {filename}")
            chunks = await self.chunk_text(cleaned_text, max_chunk_size, overlap_size)
            logger.info(f"Generating embeddings for {len(chunks)} chunks from {filename}")
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.generate_embeddings(chunk_texts)
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    **chunk,
                    "embedding": embeddings[i],
                    "filename": filename,
                    "file_size": len(file_content),
                    "original_text_length": len(text),
                    "cleaned_text_length": len(cleaned_text)
                })
            return {
                "filename": filename,
                "file_size": len(file_content),
                "original_text": text,
                "cleaned_text": cleaned_text,
                "total_chunks": len(processed_chunks),
                "chunks": processed_chunks,
                "processing_successful": True,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error in complete document processing for {filename}: {e}")
            return {
                "filename": filename,
                "file_size": len(file_content) if file_content else 0,
                "original_text": "",
                "cleaned_text": "",
                "total_chunks": 0,
                "chunks": [],
                "processing_successful": False,
                "error": str(e)
            }

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return list(self.supported_formats.keys())

    def load_pdf_as_different_pages(self, folder_path: str) -> List[Any]:
        """
        Load PDFs from folder, treating each page as a separate document.
        """
        docs = []
        if not os.path.isdir(folder_path):
            print(f"Error: Directory not found at '{folder_path}'")
            return docs
        for item_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item_name)
            if os.path.isfile(full_path) and item_name.lower().endswith('.pdf'):
                try:
                    loader = PyMuPDFLoader(full_path)
                    documents = loader.load()
                    docs.extend(documents)
                except Exception as e:
                    print(f"Failed to load {item_name}: {e}")
        return docs

    # ---------------------------
    # Improved Sonnet Functions
    # ---------------------------
    async def _sonnet_clean_text_advanced(self, text: str) -> str:
        """
        Improved text cleaning with better preprocessing and normalization.
        Uses spaCy for lemmatization and stopword removal.
        """
        try:
            if not text or len(text.strip()) == 0:
                return ""
            text = text.strip()
            text = text.replace('\u2018', "'").replace('\u2019', "'")
            text = text.replace('\u201c', '"').replace('\u201d', '"')
            text = text.replace('\u2013', '-').replace('\u2014', '-')
            text = text.replace('\u00a0', ' ')
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\\\n]', ' ', text)
            if self.nlp_model:
                doc = self.nlp_model(text)
                cleaned_tokens = []
                for token in doc:
                    if not token.is_stop and not token.is_punct and len(token.text.strip()) > 1:
                        cleaned_tokens.append(token.lemma_.lower())
                cleaned_text = " ".join(cleaned_tokens)
                if len(cleaned_text) < len(text) * 0.3:
                    return self._basic_clean_text(text)
                return cleaned_text
            else:
                return self._basic_clean_text(text)
        except Exception as e:
            logger.error(f"Error in advanced text cleaning: {e}")
            return self._basic_clean_text(text)

    async def _sonnet_chunk_text_intelligent(self, text: str, max_chunk_size: int = 1000, 
                                           overlap_size: int = 200, min_chunk_size: int = 100) -> List[Dict[str, Any]]:
        """
        Improved text chunking with intelligent boundary detection.
        Tries to split at paragraphs, sentences, or word boundaries.
        """
        try:
            if len(text) <= max_chunk_size:
                return [{
                    "chunk_id": str(uuid.uuid4()),
                    "text": text,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "start_pos": 0,
                    "end_pos": len(text),
                    "token_count": len(text.split())
                }]
            chunks = []
            start = 0
            chunk_index = 0
            boundary_patterns = [
                r'\n\n+',      # Paragraph breaks
                r'\. [A-Z]',   # Sentence endings followed by capital letter
                r'[.!?]\s+',   # Any sentence ending
                r'\n',         # Line breaks
                r'[,;]\s+',    # Clause breaks
                r'\s+'         # Word boundaries
            ]
            while start < len(text):
                end = min(start + max_chunk_size, len(text))
                if end < len(text):
                    best_boundary = end
                    for pattern in boundary_patterns:
                        search_start = max(start + min_chunk_size, end - 200)
                        search_text = text[search_start:end]
                        matches = list(re.finditer(pattern, search_text))
                        if matches:
                            last_match = matches[-1]
                            boundary_pos = search_start + last_match.end()
                            if boundary_pos > start + min_chunk_size:
                                best_boundary = boundary_pos
                                break
                    end = best_boundary
                chunk_text = text[start:end].strip()
                if chunk_text and len(chunk_text) >= min_chunk_size:
                    chunks.append({
                        "chunk_id": str(uuid.uuid4()),
                        "text": chunk_text,
                        "chunk_index": chunk_index,
                        "total_chunks": 0,
                        "start_pos": start,
                        "end_pos": end,
                        "token_count": len(chunk_text.split())
                    })
                    chunk_index += 1
                start = max(start + 1, end - overlap_size)
                if start >= len(text):
                    break
            total_chunks = len(chunks)
            for chunk in chunks:
                chunk["total_chunks"] = total_chunks
            return chunks
        except Exception as e:
            logger.error(f"Error in intelligent chunking: {e}")
            return await self.chunk_text(text, max_chunk_size, overlap_size)

    async def _sonnet_generate_embeddings_batched(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Improved embedding generation with batching for better performance.
        """
        try:
            if not texts:
                return []
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                loop = asyncio.get_event_loop()
                batch_embeddings = await loop.run_in_executor(
                    None, self.embedding_text, batch
                )
                all_embeddings.extend(batch_embeddings)
            return all_embeddings
        except Exception as e:
            logger.error(f"Error in batched embedding generation: {e}")
            return await self.generate_embeddings(texts)

# ---------------------------
# DocumentHandler Class
# ---------------------------
class DocumentHandler:
    """
    Helper class for chunk ID generation and ChromaDB preparation.
    """
    def __init__(self, doc_manager: Optional[MustanDocumentManager] = None):
        self.doc_manager = doc_manager or MustanDocumentManager()

    def generate_chunk_id(self, chat_id: str, chunk_index: int, filename: str = "") -> str:
        """Generate unique chunk ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_id = f"{chat_id}_{timestamp}_{chunk_index}"
        if filename:
            file_part = re.sub(r'[^\w\-_\.]', '_', filename)[:20]
            base_id = f"{file_part}_{base_id}"
        return base_id

    async def check_document_type(self, filename: str) -> str:
        """Check and return document type."""
        ext = os.path.splitext(filename.lower())[1]
        type_mapping = {
            '.pdf': 'pdf',
            '.docx': 'word',
            '.txt': 'txt'
        }
        return type_mapping.get(ext, 'unsupported')

    async def process_documents_for_chromadb(self, documents: List[Dict[str, Any]], 
                                           chat_id: str, max_chunk_size: int = 1000, 
                                           overlap_size: int = 200) -> List[Dict[str, Any]]:
        """
        Process documents and prepare them for ChromaDB storage.
        Returns list of chunks ready for ChromaDB.
        """
        chromadb_chunks = []
        for doc in documents:
            try:
                filename = doc.get('filename', 'unknown')
                file_content = doc.get('content', b'')
                if not file_content:
                    continue
                original_text = await self.doc_manager.extract_text_from_file(file_content, filename)
                if hasattr(self.doc_manager, '_sonnet_clean_text_advanced'):
                    cleaned_text = await self.doc_manager._sonnet_clean_text_advanced(original_text)
                else:
                    cleaned_text = await self.doc_manager.clean_text(original_text)
                if hasattr(self.doc_manager, '_sonnet_chunk_text_intelligent'):
                    chunks = await self.doc_manager._sonnet_chunk_text_intelligent(
                        cleaned_text, max_chunk_size, overlap_size
                    )
                else:
                    chunks = await self.doc_manager.chunk_text(cleaned_text, max_chunk_size, overlap_size)
                chunk_texts = [chunk["text"] for chunk in chunks]
                if hasattr(self.doc_manager, '_sonnet_generate_embeddings_batched'):
                    embeddings = await self.doc_manager._sonnet_generate_embeddings_batched(chunk_texts)
                else:
                    embeddings = await self.doc_manager.generate_embeddings(chunk_texts)
                for i, chunk in enumerate(chunks):
                    chunk_id = self.generate_chunk_id(chat_id, i, filename)
                    start_pos = chunk.get('start_pos', 0)
                    end_pos = chunk.get('end_pos', len(original_text))
                    original_chunk_text = original_text[start_pos:end_pos]
                    chromadb_chunk = {
                        "chunk_id": chunk_id,
                        "chunk_metadata": {
                            "filename": filename,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "start_pos": start_pos,
                            "end_pos": end_pos,
                            "token_count": chunk.get('token_count', len(chunk["text"].split())),
                            "chat_id": chat_id,
                            "created_at": datetime.now().isoformat()
                        },
                        "embeddings": embeddings[i],
                        "doctext": original_chunk_text
                    }
                    chromadb_chunks.append(chromadb_chunk)
            except Exception as e:
                logger.error(f"Error processing document {doc.get('filename', 'unknown')}: {e}")
                continue
        return chromadb_chunks

# ---------------------------
# Standalone Async Functions
# ---------------------------
async def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Standalone function for text extraction."""
    manager = MustanDocumentManager()
    return await manager.extract_text_from_file(file_content, filename)

async def clean_text(text: str) -> str:
    """Standalone function for text cleaning."""
    manager = MustanDocumentManager()
    return await manager.clean_text(text)

async def chunk_text(text: str, max_chunk_size: int = 1000, overlap_size: int = 200) -> List[Dict[str, Any]]:
    """Standalone function for text chunking."""
    manager = MustanDocumentManager()
    return await manager.chunk_text(text, max_chunk_size, overlap_size)

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Standalone function for embedding generation."""
    manager = MustanDocumentManager()
    return await manager.generate_embeddings(texts)

# ---------------------------
# Example Usage & Testing
# ---------------------------
if __name__ == "__main__":
    async def test_document_manager():
        manager = MustanDocumentManager()
        sample_text = "This is a test document. It contains multiple sentences. We will test text processing capabilities."
        print("Original text:", sample_text)
        cleaned = await manager.clean_text(sample_text)
        print("Cleaned text:", cleaned)
        chunks = await manager.chunk_text(sample_text, max_chunk_size=50, overlap_size=10)
        print("Chunks:", len(chunks))
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i}: {chunk['text'][:50]}...")
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = await manager.generate_embeddings(chunk_texts)
        print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

    asyncio.run(test_document_manager())