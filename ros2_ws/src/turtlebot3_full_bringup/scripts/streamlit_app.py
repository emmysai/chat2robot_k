import streamlit as st

from chatbot import ask_agent


st.title("Chat2Robot")

if "messages" not in st.session_state:
    st.session_state.messages = []


# Bisherige Nachrichten anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Neue Eingabe
user_input = st.chat_input("Was soll der Roboter machen?")

if user_input:

    # User-Nachricht anzeigen und speichern
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)


    # Agent aufrufen
    response = ask_agent(user_input)


    # Bot-Antwort anzeigen und speichern
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.write(response)