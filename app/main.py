import streamlit as st
from app.agent.agent import get_agent

st.set_page_config(page_title="AgriAssist AI")

st.title("🌾 AgriAssist AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

llm = get_agent()

user_input = st.chat_input("Ask your farming question")

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    response = llm.invoke(user_input)

    st.session_state.messages.append(
        {"role": "assistant", "content": response.content}
    )

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])