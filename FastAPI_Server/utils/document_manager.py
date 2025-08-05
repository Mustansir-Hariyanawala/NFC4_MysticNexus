import os
import re
import io
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import asyncio
import logging

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize document manager with embedding model"""
        self.embedding_model = SentenceTransformer(model_name)
        self.stop_words = set(stopwords.words('english'))
        
        # Supported file formats
        self.supported_formats = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
    
    def _is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.supported_formats
    
    async def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded file based on its format"""
        try:
            ext = os.path.splitext(filename.lower())[1]
            
            if ext == '.pdf':
                return await self._extract_from_pdf(file_content)
            elif ext == '.docx':
                return await self._extract_from_docx(file_content)
            elif ext == '.txt':
                return file_content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file format: {ext}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise
    
    async def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    async def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
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
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        try:
            # Basic cleaning
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines
            text = text.strip()
            
            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            filtered_tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
            
            # Rejoin tokens
            cleaned_text = ' '.join(filtered_tokens)
            
            # If cleaned text is too short, return original text
            if len(cleaned_text) < 50:
                return text
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text  # Return original text if cleaning fails
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        try:
            if len(text) <= chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + chunk_size
                
                # Try to end at a sentence boundary
                if end < len(text):
                    # Look for sentence endings
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end > start + chunk_size // 2:
                        end = sentence_end + 1
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                start = end - overlap
                
                # Prevent infinite loop
                if start >= len(text):
                    break
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            return [text]  # Return original text as single chunk
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            # Run embedding generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self.embedding_model.encode, text
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return list(self.supported_formats.keys())
