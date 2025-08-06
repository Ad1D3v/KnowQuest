import asyncio
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

# Handle the LangChain-Streamlit Sync
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Import Custom Module
import kqt_core as kqc

# Define Page Setup
st.set_page_config(page_title="KnowQuest", page_icon="🕵️‍♂️")
st.title("KnowQuest")
st.subheader("Your Journey to Smarter Insights.")

## Define Sidebar Interface
with st.sidebar:
    st.header("Interface")
    website_url = st.text_input(label = "Article Link", placeholder = "Enter Article URL..", key = "user_input")
    process_urls = st.sidebar.button('Process Article')

# Handle the Inputs and Data Ingestion
if process_urls:
    if website_url is None or website_url == "":
        st.info("Nothing to Process...⚠️⚠️⚠️")

    else:
        with st.spinner("Processing Data...🔄🔄🔄"):
            st.session_state.vector_store = kqc.get_vectorstore_from_url(website_url)
        st.info("New Data Ingested...✅✅✅")
       

if 'vector_store' in st.session_state:
    # Check if History Exists and Initialize
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I am KnowQuest. How can I help you?"),
        ]

    # Handle the Conversation and Add to History
    user_query = st.chat_input("Enter your Query...")
    if user_query is not None and user_query != "":
        response = kqc.get_response(user_query, st.session_state)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    # Handle the Conversation History
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)