
from langchain_community.document_loaders import PyMuPDFLoader
import os
import spacy
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

import os
# Make sure you have the necessary import, for example:
# from langchain_community.document_loaders import PyMuPDFLoader

def load_pdf_as_different_pages(folder_path: str):
    """
    Loads all PDF files from a specified folder, treating each page as a separate document.

    Args:
        folder_path: The path to the folder containing PDF files.

    Returns:
        A list of documents, where each document is a page from a PDF.
    """
    docs = []
    # Check if the directory exists to avoid errors
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at '{folder_path}'")
        return docs

    for item_name in os.listdir(folder_path):
        # Create the full, correct path to the item
        full_path = os.path.join(folder_path, item_name)
        
        # Check if it's a file and has a .pdf extension
        if os.path.isfile(full_path) and item_name.lower().endswith('.pdf'):
            try:
                #import important
                loader = PyMuPDFLoader(full_path)
                documents = loader.load()
                docs.extend(documents)
            except Exception as e:
                print(f"Failed to load {item_name}: {e}")
                
    return docs

def document_object_to_text(documents):
    list_of_texts = []
    for doc in documents:
        list_of_texts.append(doc.page_content)
    return list_of_texts

# import important

# Install spacy using the following command:
# pip install -U pip setuptools wheel
# pip install -U spacy
# python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

def clean_text_efficiently(texts, model):
    """
    Removes stopwords and punctuation from a list of texts efficiently.

    Args:
        texts (list): A list of strings to process.
        model: The pre-loaded spaCy language model.

    Returns:
        A list of cleaned texts.
    """

    
    processed_texts = []
    # Process texts as a stream
    for doc in model.pipe(texts):
        # Keep a token if it is NOT a stopword AND NOT punctuation
        filtered_text = " ".join(
            token.text for token in doc if not token.is_stop and not token.is_punct
        )
        processed_texts.append(filtered_text)
    
    return processed_texts

# import important
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
def embedding_text(texts):
    return embeddings.embed_documents(texts)
    
# Example usage:


if __name__ == "__main__":
    document_list = load_pdf_as_different_pages("C:\mustansir\House Of Code\Python\CampusX\langchain-rag-tutorial-main\data_cleaning")
    text_list = document_object_to_text(document_list)
    cleaned_texts_list = clean_text_efficiently(text_list, nlp)
    embeddings = embedding_text(cleaned_texts_list)
    print(embeddings ,len(embeddings))
    