import streamlit as st
import ollama
import json

# ---------------------------
# Load JSON data
# ---------------------------
with open("qa_data.json", "r") as f:
    qa_data = json.load(f)

# ---------------------------
# Matching function
# ---------------------------
def find_answer(user_input):
    user_input = user_input.lower()

    for item in qa_data:
        # Check main question
        if user_input in item["question"].lower():
            return item["answer"]

        # Check variations
        for var in item.get("variations", []):
            if user_input in var["question"].lower():
                return var["answer"]

    return None

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Electricity Authority Chatbot")
st.title("Electricity Authority Chatbot")

# ---------------------------
# System prompt
# ---------------------------
SYSTEM_PROMPT = """
You are a professional customer support assistant for an Electricity Authority.

Rules:
- Answer clearly and politely.
- Be short and helpful.
- If unsure, say the issue will be forwarded to customer service.
"""

# ---------------------------
# Session memory
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Display chat history
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# User input
# ---------------------------
if prompt := st.chat_input("Ask your question here.."):

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # ---------------------------
    # Generate response
    # ---------------------------
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 🔍 Step 1: Try JSON match
        answer = find_answer(prompt)

        # ✅ If found → use JSON answer
        if answer:
            full_response = answer
            message_placeholder.markdown(full_response)

        # 🤖 If not found → fallback to Ollama
        else:
            try:
                stream = ollama.chat(
                    model="phi3",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    stream=True,
                    options={
                        "num_predict": 150,
                        "temperature": 0.3
                    }
                )

                for chunk in stream:
                    full_response += chunk["message"]["content"]
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

            except:
                # 🚨 If Ollama fails
                full_response = "Sorry, I will forward your issue to customer service."
                message_placeholder.markdown(full_response)

    # Save assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )