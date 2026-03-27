import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def get_answer_from_documents(query: str, index_save_path: str = "faiss_index"):
    """
    Retrieves context from FAISS and generates an answer using modern LCEL syntax.
    """
    # 1. Initialize Embeddings
    # --- OPTION A: Google Gemini Embeddings (Active) ---
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # 2. Load the FAISS database
    try:
        vector_store = FAISS.load_local(
            index_save_path, 
            embeddings, 
            allow_dangerous_deserialization=True 
        )
    except Exception as e:
        return f"Error loading documents. Details: {e}"

    # 3. Create the retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. Initialize the LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    # 5. Define the Prompt Template
    template = """You are an intelligent educational assistant. 
    Use the following pieces of retrieved context to answer the student's question. 
    If the answer is not in the context, clearly state that you don't know based on the uploaded documents. 
    Keep your explanations clear, conceptual, and provide step-by-step breakdowns where necessary.

    Context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 6. Helper function to format retrieved documents into a single string
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 7. Build the Bulletproof LCEL Chain
    # This pipes the data directly: Retriever -> Format -> Prompt -> LLM -> String Output
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 8. Execute
    print(f"Querying the tutor: '{query}'...")
    response = rag_chain.invoke(query)
    
    return response