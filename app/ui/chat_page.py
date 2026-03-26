import time
import streamlit as st
from bson import ObjectId

from app.agent.agent import get_agent
from app.agent.title_generation import generate_chat_title

from app.utils.chat_history import build_chat_history

from app.database.chat_repository import (
    create_conversation,
    add_message,
    get_messages,
    get_user_conversations,
    update_conversation_title
)
from app.memory.conversation_memory import ConversationMemory


def show_chat_page(cookies):

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

    st.title("AI tutor")

    # ---------------- SIDEBAR ----------------
    with st.sidebar:

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


        conversations = get_user_conversations(
            st.session_state.user["_id"]
        )

        title_col, button_col = st.columns([5, 2])

        with title_col:
            st.subheader(f"Your Chats ({len(conversations)})")

        with button_col:
            if st.button("➕", help="New Chat"):
                st.session_state.conversation_id = None
                st.query_params.clear()
                st.rerun()

        # -------- CHAT LIST --------
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
                st.query_params["chat"] = str(convo["_id"])
                st.rerun()

    # ---------------- LLM ----------------
    memory = ConversationMemory()
    user_memories = memory.get_memories(str(st.session_state.user["_id"]))
    llm = get_agent(memories=user_memories)

    # ---------------- EMPTY STATE ----------------
    if st.session_state.conversation_id is None:
        st.info("Start a new conversation by asking a question.")

    # ---------------- LOAD & DISPLAY HISTORY ----------------
    if st.session_state.conversation_id:

        messages = get_messages(st.session_state.conversation_id)

        for msg in messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # ---------------- INPUT ----------------
    user_input = st.chat_input("Ask your farming question")

    if user_input:

        is_new_conversation = False

        # -------- CREATE CONVO IF NEW --------
        if st.session_state.conversation_id is None:

            conversation_id = create_conversation(
                st.session_state.user["_id"]
            )

            st.session_state.conversation_id = conversation_id
            st.query_params["chat"] = str(conversation_id)

            is_new_conversation = True

        conversation_id = st.session_state.conversation_id

        # -------- SHOW USER MESSAGE --------
        with st.chat_message("user"):
            st.write(user_input)

        # -------- ASSISTANT RESPONSE --------
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🌱"):

                # ✅ ALWAYS FETCH LATEST HISTORY
                history = get_messages(conversation_id)

                # ✅ BUILD CONTEXT (LAST N MESSAGES)
                chat_history = build_chat_history(history)
                
                # ---------------- SAVE MEMORY ----------------
                memory.extract_and_save_facts(str(st.session_state.user["_id"]), user_input)

                # ✅ ADD CURRENT USER INPUT (Translated to English for AI)
                chat_history.append(("user", user_input))

                # ✅ CALL AGENT
                print(f"Chat History (English): {chat_history}")
                result = llm.invoke({"messages": chat_history})
                
                answer = result["messages"][-1].content

                st.write(answer)

        # -------- SAVE USER MESSAGE --------
        add_message(conversation_id, "user", user_input)

        # -------- SAVE ASSISTANT MESSAGE --------
        add_message(conversation_id, "assistant", answer)

        # -------- TITLE GENERATION --------
        if is_new_conversation:
            title = generate_chat_title(user_input)
            update_conversation_title(conversation_id, title)

        # -------- RERUN --------
        st.rerun()