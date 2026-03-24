# 📚 Multimodal AI Tutor  

Multimodal AI Tutor is an intelligent educational assistant designed to help students learn from textbooks, lecture notes, and visual materials through natural language interaction.

The system leverages a **Retrieval-Augmented Generation (RAG)** architecture combined with a **multimodal Large Language Model (LLM)** to provide accurate, context-aware explanations from both textual and visual content.

Instead of relying only on pretrained knowledge, the system retrieves relevant information from uploaded documents and integrates it into responses, enabling grounded and reliable answers.

The application is implemented as a **Streamlit-based chat interface** with a Python backend orchestrated using LangChain.

---

# 🚀 Key Features  

## 🎓 Conversational AI Tutor  
Users can ask educational queries such as:

- Explain photosynthesis  
- What is normalization in DBMS?  
- Derive Ohm’s Law  
- Explain the diagram in this chapter  

The assistant provides:
- Clear explanations  
- Step-by-step reasoning  
- Context-aware answers  

---

## 📚 Retrieval-Augmented Generation (RAG)  

The system retrieves relevant information from uploaded study materials:

- Documents are processed into chunks  
- Converted into embeddings  
- Stored in a vector database (FAISS)  
- Relevant content is retrieved and passed to the LLM  

This ensures:
- Higher accuracy  
- Reduced hallucination  
- Context-grounded responses  

---

## 🖼️ Multimodal Understanding  

The system supports both **text and visual content**:

- Extracts diagrams and images from PDFs  
- Generates captions using a multimodal model  
- Stores captions alongside text for retrieval  

This allows the tutor to:
- Explain diagrams in simple terms  
- Answer questions involving visual concepts  

---

## 📷 Diagram Explanation (Direct Input)  

Users can upload images such as:
- Diagrams  
- Charts  
- Screenshots  

The system uses multimodal LLM capabilities to:
- Interpret the image  
- Provide step-by-step explanations  

---

## ❓ Practice Question Generation  

The tutor can generate:
- MCQs  
- Short answer questions  
- Conceptual questions  

Based on retrieved content, helping reinforce learning.

---

## 🔄 Session-Based Context  

- Each chat session maintains its own document context  
- Users can upload notes per session  
- Queries are answered based on that session’s knowledge base  

---

## 🌐 Web Search Fallback  

If no documents are available:
- The system falls back to web search  
- Retrieves and summarizes relevant information  

---

# 🏗️ System Architecture  

**User Input**  
↓  
**Input Type Detection**  

- Image → Multimodal LLM  
- Documents Available → RAG Pipeline  
- Else → Web Search  

↓  
**LLM Response**  

---

# ⚙️ Technology Stack  

**Language**  
- Python  

**Frontend**  
- Streamlit  

**Backend / Orchestration**  
- LangChain  

**LLM**  
- Google Gemini API  

**Embeddings**  
- SentenceTransformers / Gemini embeddings  

**Vector Database**  
- FAISS  

**Database**  
- MongoDB  

**Storage**  
- Cloudinary / AWS S3 (for documents)  

**APIs**  
- Web Search API  

---

# 📂 Repository Structure  

```
ai-tutor/
│
├── app/
│ ├── main.py
│ ├── config.py
│
│ ├── agent/
│ │ ├── agent.py
│ │ └── tools_registry.py
│
│ ├── rag/
│ │ ├── ingestion.py
│ │ ├── retriever.py
│ │ └── vector_store.py
│
│ ├── multimodal/
│ │ ├── image_captioning.py
│ │ └── image_handler.py
│
│ ├── auth/
│ ├── database/
│ ├── memory/
│ ├── models/
│
├── docker/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🛠️ Development Setup  

## 1. Install uv  

```bash
pip install uv
```
2. Clone Repository
```bash
git clone <repository-url>
cd ai-tutor
```
3. Install Dependencies
```bash
uv sync
```
4. Configure Environment Variables

Create a .env file and add necessary stuff

5. Run Application
```bash
uv run python -m streamlit run app/main.py
```

App runs on:
http://localhost:8501

# Managing Dependencies

This project uses **uv** for dependency management.  
Do **not** use `pip install` directly.

---

## Add a New Dependency

To install a new package:

```bash
uv add package-name
```

Example:

```bash
uv add pandas
```

This will automatically:

- install the package
- update `pyproject.toml`
- update `uv.lock`

---

## Add a Development Dependency

For development tools such as testing, linting, or formatting:

```bash
uv add --dev package-name
```

Example:

```bash
uv add --dev pytest ruff black
```

# Development Workflow

Each developer should work on a separate branch:

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Implemented feature"
git push origin feature/your-feature
```

Then create a Pull Request.

# Notes

This project demonstrates RAG + Multimodal AI integration
Designed for educational use cases
Scalable architecture for real-world applications