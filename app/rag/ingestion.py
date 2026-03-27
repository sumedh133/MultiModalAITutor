import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Uncomment the line below if the team decides to test Sentence Transformers
# from langchain_community.embeddings import HuggingFaceEmbeddings 

def process_and_store_document(file_path: str, index_save_path: str = "faiss_index"):
    """
    Extracts text from a PDF, chunks it, generates embeddings, 
    and stores it in a FAISS vector database.
    """
    print(f"Starting ingestion for: {file_path}")

    # 1. Document Upload -> Text Extraction
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"Extracted {len(documents)} pages.")

    # 2. Text Chunking
    # chunk_overlap ensures context isn't lost if a sentence gets cut in half
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # 3. Embeddings Strategy
    
    # --- OPTION A: Google Gemini Embeddings (Active) ---
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # --- OPTION B: Sentence Transformers (Alternative) ---
    # To test this, comment out Option A, uncomment the import at the top, 
    # and uncomment the line below.
    # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Create and Store in FAISS
    print("Generating embeddings and building FAISS index...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save the index locally so it can be retrieved by the chatbot later
    vector_store.save_local(index_save_path)
    print(f"FAISS index successfully saved to /{index_save_path}")

    return vector_store