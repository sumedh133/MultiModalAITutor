import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def process_and_store_document(
    conversation_id: str,
    file_path: str = None,
    raw_text: str = None,
    base_path: str = "faiss_index"
):
    """
    Process PDF or raw text and store embeddings in a conversation-specific FAISS index
    """

    if not file_path and not raw_text:
        raise ValueError("Either file_path or raw_text must be provided")

    print(f"Starting ingestion for conversation: {conversation_id}")

    # ✅ Create folder per conversation
    index_path = os.path.join(base_path, conversation_id)
    os.makedirs(index_path, exist_ok=True)

    # -------------------------------
    # 1. Load data
    # -------------------------------
    if file_path:
        print(f"Processing PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"Extracted {len(documents)} pages.")

    else:
        print("Processing raw text (image or direct input)")
        documents = [
            Document(page_content=raw_text, metadata={"source": "image"})
        ]

    # -------------------------------
    # 2. Chunking
    # -------------------------------
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # -------------------------------
    # 3. Embeddings
    # -------------------------------
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    # -------------------------------
    # 4. Load or create FAISS
    # -------------------------------
    faiss_file = os.path.join(index_path, "index.faiss")

    if os.path.exists(faiss_file):
        print("Loading existing FAISS index...")
        vector_store = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        vector_store.add_documents(chunks)
    else:
        print("Creating new FAISS index...")
        vector_store = FAISS.from_documents(chunks, embeddings)

    # -------------------------------
    # 5. Save
    # -------------------------------
    vector_store.save_local(index_path)
    print(f"Saved FAISS index at {index_path}")

    return vector_store