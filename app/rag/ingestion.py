
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


def process_and_store_document(
    file_path: str,
    conversation_id: str,
    base_path: str = "faiss_index"
):
    """
    Process PDF and store embeddings in a conversation-specific FAISS index
    """

    print(f"Starting ingestion for: {file_path}")

    # ✅ Create folder per conversation
    index_path = os.path.join(base_path, conversation_id)
    os.makedirs(index_path, exist_ok=True)

    # 1. Load PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"Extracted {len(documents)} pages.")

    # 2. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 3. Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    # 4. Load existing index OR create new
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        print("Loading existing FAISS index...")
        vector_store = FAISS.load_local(index_path, embeddings,allow_dangerous_deserialization=True)
        vector_store.add_documents(chunks)
    else:
        print("Creating new FAISS index...")
        vector_store = FAISS.from_documents(chunks, embeddings)

    # 5. Save
    vector_store.save_local(index_path)
    print(f"Saved FAISS index at {index_path}")

    return vector_store

