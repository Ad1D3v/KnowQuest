import os
import getpass
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma

# Handle Environment Variables
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")
if "MODEL_NAME" not in os.environ:
    os.environ["MODEL_NAME"] = getpass.getpass("Enter your Model Name: ")

# Define the Model
llm = ChatGoogleGenerativeAI(
    model = os.environ.get("MODEL_NAME"),
    temperature=0.6,
    max_retries=2
)

# Define the Embeddings Model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Handle the Vector Store
def get_vectorstore_from_url(url):
    # Get the Text in Document form
    loader = WebBaseLoader(url)
    document = loader.load()
    
    # Split the Document into Chunks then Create a Vectorstore
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)
    vector_store = Chroma.from_documents(document_chunks, embeddings)

    return vector_store

# Handle the Retriever
def get_context_retriever_chain(vector_store):
    
    # Define the Retriever
    retriever = vector_store.as_retriever()
    
    # Define the Template for Retriever
    prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
      ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    # Create the Retriever Chain
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    return retriever_chain

# Handle the RAG Conversation
def get_conversational_rag_chain(retriever_chain): 
    
    # Define the Template
    prompt = ChatPromptTemplate.from_messages([
      ("system", "Answer the user's questions based on the below context:\n\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
    ])

    # Create the Chain
    stuff_documents_chain = create_stuff_documents_chain(llm,prompt)
    
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

# Handle Response
def get_response(user_input, session_state):
    retriever_chain = get_context_retriever_chain(session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    
    # Invoke the Chain for Response Generation
    response = conversation_rag_chain.invoke({
        "chat_history": session_state.chat_history,
        "input": user_input
    })
    
    return response['answer']