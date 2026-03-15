import streamlit as st
from app.ui.auth_page import show_auth_page
from app.ui.chat_page import show_chat_page
from app.database.health_check import check_database_connection

st.set_page_config(page_title="AgriAssist AI")

if not check_database_connection():
        st.error("Database connection failed")
        st.stop()

if "token" not in st.session_state:
    st.session_state.token = None

if st.session_state.token is None:
    show_auth_page()
else:
    show_chat_page()