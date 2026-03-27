import streamlit as st
import os
import tempfile
from streamlit_cookies_manager import EncryptedCookieManager 
from app.database.health_check import check_database_connection
from app.auth.jwt_handler import decode_token
from app.ui.auth_page import show_auth_page
from app.ui.chat_page import show_chat_page
from app.database.user_repository import UserRepository

# --- IMPORT THE RAG INGESTION FUNCTION ---
from app.rag.ingestion import process_and_store_document

import warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning) 
warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(page_title="AI tutor")

cookies = EncryptedCookieManager(
    prefix="AI tutor",
    password="super_secret_cookie_key"
)

if not cookies.ready():
    st.stop()


# --------------------------------------------------
# Restore Session From Cookie (Auto Login)
# --------------------------------------------------

if "token" not in st.session_state and not st.session_state.get("logout", False):

    cookie_token = cookies.get("auth_token")

    # Only restore if cookie has a real token
    if cookie_token and cookie_token != "LOGGED_OUT":

        user_id = decode_token(cookie_token)

        if user_id:

            repo = UserRepository()
            user = repo.get_user_by_id(user_id)

            if user:
                st.session_state.token = cookie_token
                st.session_state.user = user


if "token" not in st.session_state:
    st.session_state.token = None

# --------------------------------------------------
# Initialize RAG Document State
# --------------------------------------------------
if "is_document_processed" not in st.session_state:
    st.session_state.is_document_processed = False


if not check_database_connection():
    st.error("Database connection failed")
    st.stop()


if st.session_state.token is None:
    # Route to login/signup if not authenticated
    show_auth_page(cookies)
else:
    # --------------------------------------------------
    # RAG Ingestion Sidebar (Only visible when logged in)
    # --------------------------------------------------
    with st.sidebar:
        st.header("📂 Study Materials")
        uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
        
        # Process the file if uploaded and not already processed
        if uploaded_file and not st.session_state.is_document_processed:
            with st.spinner("Analyzing document and building knowledge base..."):
                # Save Streamlit file to a temp physical file for PyPDFLoader
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    process_and_store_document(tmp_path)
                    st.session_state.is_document_processed = True
                    st.success("✅ Document processed successfully! You can now ask questions.")
                except Exception as e:
                    st.error(f"Error processing document: {e}")
                finally:
                    # Clean up the temporary file from the system
                    os.remove(tmp_path)

    # Route to the main chat interface
    show_chat_page(cookies)