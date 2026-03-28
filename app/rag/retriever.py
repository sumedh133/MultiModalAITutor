
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def get_answer_from_documents(
    query: str,
    conversation_id: str,
    base_path: str = "faiss_index"
):
    """
    Retrieves context from a conversation-specific FAISS index
    """

    # ✅ Build correct path
    index_path = os.path.join(base_path, conversation_id)

    # 1. Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    # 2. Load FAISS (conversation-specific)
    if not os.path.exists(index_path):
        return "No documents uploaded for this chat yet."

    try:
        vector_store = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        return f"Error loading documents: {e}"

    # 3. Retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    # 5. Prompt
    template = """You are an intelligent educational assistant. 
Use the following context to answer the student's question. 
If the answer is not in the context, say you don't know based on the uploaded documents.

Context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)

    # 6. Formatter
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 7. Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 8. Execute
    response = rag_chain.invoke(query)

    return response

