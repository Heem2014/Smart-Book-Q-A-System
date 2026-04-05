"""
rag_tool.py - Custom CrewAI tool that queries ChromaDB

This is the tool that Agent 1 (Document Retriever) uses.
It searches the vector store and returns the top 3 most relevant chunks.

How it works:
1. Takes the user's question as input
2. Converts the question into an embedding
3. Searches ChromaDB for the 3 closest matching chunks
4. Returns those chunks with their source info
"""

import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load dotenv only if available (not needed on Streamlit Cloud)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@st.cache_resource
def get_vector_store():
    """Cache the vector store connection to avoid reloading on every query."""
    if not os.path.exists("chroma_db"):
        return None
        
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

def rag_search_tool(query: str) -> str:
    """
    Search the document knowledge base for information related to the query.
    Returns the top 3 most relevant text chunks from the uploaded documents.
    """
    vector_store = get_vector_store()
    
    if not vector_store:
        return "Error: No vector store found. Please run 'python rag_setup.py' first."

    # Search for the 3 most relevant chunks (semantic search)
    results = vector_store.similarity_search(query, k=3)

    # If nothing was found, let the agent know
    if not results:
        return "No relevant information found in the documents."

    # Format the results so the agent can read them easily
    output = "Here are the top 3 relevant chunks from the document:\n"

    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        output += f"\n--- Chunk {i} (Source: {source}, Page: {page}) ---\n"
        output += doc.page_content + "\n"

    return output
