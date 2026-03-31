
import time
import streamlit as st
from bson import ObjectId
import os
import tempfile

from app.agent.agent import get_agent
from app.agent.generation import generate_chat_title, process_image
from app.rag.ingestion import process_and_store_document
from app.utils.extract_text import extract_text
from app.utils.hash import get_file_hash
from app.utils.chat_history import build_chat_history
from app.database.chat_repository import (
    create_conversation,
    add_message,
    get_messages,
    get_user_conversations,
    update_conversation_title
)
from app.memory.conversation_memory import ConversationMemory

MAX_TOTAL_SIZE_MB = 10
MAX_IMAGES = 2
MAX_PDFS = 1


def show_chat_page(cookies):

    # --------------------------------------------------
    # Initialize states
    # --------------------------------------------------

    if "reset_uploader" not in st.session_state:
        st.session_state.reset_uploader = False
        
    # ---------------- INIT ----------------
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}

    # ---------------- STYLES ----------------
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 42px;
        padding: 0 10px;
    }

    .stButton > button div,
    .stButton > button p {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        margin: 0;
    }

    button[kind="secondary"] {
        padding: 0 10px !important;
    }
    
    .profile-block {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .profile-label {
        font-size: 12px;
        opacity: 0.7;
    }

    .profile-email {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- RESTORE STATE ----------------
    params = st.query_params

    if "conversation_id" not in st.session_state:
        if "chat" in params:
            st.session_state.conversation_id = ObjectId(params["chat"])
        else:
            st.session_state.conversation_id = None

    st.title("📚 AI Tutor Chat")

    # ---------------- SIDEBAR ----------------
    with st.sidebar:

        # ---------------- PROFILE ----------------
        profile_col, logout_col = st.columns([5, 2])

        with profile_col:
            st.markdown(
                f"""
                <div class="profile-block">
                    <div class="profile-label">Profile</div>
                    <div class="profile-email" title="{st.session_state.user['email']}">
                        {st.session_state.user['email']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with logout_col:
            if st.button("↩️", help="Logout"):
                cookies["auth_token"] = "LOGGED_OUT"
                cookies.save()
                time.sleep(0.3)

                st.query_params.clear()
                st.session_state.clear()
                st.session_state.logout = True
                st.rerun()

        st.divider()

        # ---------------- DOCUMENT UPLOAD ----------------
        st.header("Study Materials")

        # 🔥 controlled reset
        uploader_key = "file_uploader"
        if st.session_state.reset_uploader:
            uploader_key = "file_uploader_reset"
            st.session_state.reset_uploader = False

        uploaded_files = st.file_uploader(
            "Upload 1 PDF + up to 2 images",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=uploader_key
        )

        # ---------------- UPLOAD HANDLER ----------------
        if uploaded_files:

            # ensure conversation exists
            if st.session_state.conversation_id is None:
                conversation_id = create_conversation(
                    st.session_state.user["_id"]
                )
                st.session_state.conversation_id = conversation_id
                st.query_params["chat"] = str(conversation_id)
            else:
                conversation_id = st.session_state.conversation_id

            convo_id = str(conversation_id)

            if convo_id not in st.session_state.processed_files:
                st.session_state.processed_files[convo_id] = set()

            # -------- FILTER NEW FILES --------
            new_files = []
            for f in uploaded_files:
                file_hash = get_file_hash(f)

                if file_hash not in st.session_state.processed_files[convo_id]:
                    new_files.append((f, file_hash))

            # 👉 nothing new → skip processing
            if not new_files:
                pass
            else:
                # -------- VALIDATION (ONLY NEW FILES) --------
                pdfs = [f for f, _ in new_files if f.type == "application/pdf"]
                images = [f for f, _ in new_files if f.type.startswith("image/")]

                total_size = sum(f.size for f, _ in new_files) / (1024 * 1024)

                if len(pdfs) > MAX_PDFS:
                    st.error("Only 1 PDF allowed")
                    st.stop()

                if len(images) > MAX_IMAGES:
                    st.error("Max 2 images allowed")
                    st.stop()

                if total_size > MAX_TOTAL_SIZE_MB:
                    st.error(f"Total upload must be under {MAX_TOTAL_SIZE_MB} MB")
                    st.stop()

                # -------- PROCESS --------
                with st.spinner("Analyzing document..."):
                    try:
                        for file, file_hash in new_files:

                            # -------- PDF --------
                            if file.type == "application/pdf":
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                                    tmp_file.write(file.getvalue())
                                    tmp_path = tmp_file.name

                                process_and_store_document(
                                    conversation_id=convo_id,
                                    file_path=tmp_path
                                )

                                os.remove(tmp_path)

                            # -------- IMAGE --------
                            elif file.type.startswith("image/"):
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                                    tmp_file.write(file.getvalue())
                                    tmp_path = tmp_file.name

                                extracted_text = process_image(tmp_path)

                                process_and_store_document(
                                    conversation_id=convo_id,
                                    raw_text=extracted_text
                                )

                                os.remove(tmp_path)

                                st.image(file, caption=file.name, use_container_width=True)

                            # ✅ mark processed
                            st.session_state.processed_files[convo_id].add(file_hash)

                        st.success("New content added to this chat!")

                    except Exception as e:
                        st.error(f"Error: {e}")
            
        st.divider()

        # ---------------- CHAT LIST ----------------
        conversations = get_user_conversations(
            st.session_state.user["_id"]
        )

        title_col, button_col = st.columns([5, 2])

        with title_col:
            st.subheader(f"Your Chats ({len(conversations)})")

        with button_col:
            if st.button("➕", help="New Chat"):
                st.session_state.conversation_id = None
                st.session_state.reset_uploader = True   # 🔥 FIX
                st.session_state.pop("messages", None)
                st.query_params.clear()
                st.rerun()

        for convo in conversations:
            title = convo.get("title", "New Chat")
            is_active = convo["_id"] == st.session_state.conversation_id

            if st.button(
                title,
                key=str(convo["_id"]),
                use_container_width=True,
                type="secondary" if is_active else "tertiary"
            ):
                st.session_state.conversation_id = convo["_id"]
                st.session_state.reset_uploader = True   # 🔥 FIX
                st.query_params["chat"] = str(convo["_id"])
                st.rerun()

    # ---------------- LLM ----------------
    memory = ConversationMemory()
    user_memories = memory.get_memories(str(st.session_state.user["_id"]))

    agent_executor = get_agent(
        memories=user_memories,
        conversation_id=str(st.session_state.conversation_id)
    )

    # ---------------- EMPTY STATE ----------------
    if st.session_state.conversation_id is None:
        st.info("Start a new conversation or upload a document to begin.")

    # ---------------- LOAD & DISPLAY HISTORY ----------------
    if st.session_state.conversation_id:
        messages = get_messages(st.session_state.conversation_id)

        for msg in messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # ---------------- INPUT ----------------
    user_input = st.chat_input("Ask a question about your study materials...")

    if user_input:

        is_new_conversation = False

        if st.session_state.conversation_id is None:
            conversation_id = create_conversation(
                st.session_state.user["_id"]
            )
            st.session_state.conversation_id = conversation_id
            st.query_params["chat"] = str(conversation_id)
            is_new_conversation = True

        conversation_id = st.session_state.conversation_id

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking... 📚"):

                history = get_messages(conversation_id)
                chat_history = build_chat_history(history)

                result = agent_executor.invoke({
                    "messages": chat_history + [("user", user_input)]
                })

                answer = extract_text(result)
                print("Agent answer:", result)
                st.write(answer)

        add_message(conversation_id, "user", user_input)
        add_message(conversation_id, "assistant", answer)

        convo = next(
            (c for c in conversations if c["_id"] == conversation_id),
            None
        )

        if convo and (not convo.get("title") or convo.get("title") == "New Chat"):
            title = generate_chat_title(user_input, assistant_response=answer)
            update_conversation_title(conversation_id, title)
            print(title)
            update_conversation_title(conversation_id, title)

        st.rerun()

