from langchain_community.chat_models import ChatOpenAI
import streamlit as st
import openai

from streamlit_chat import message
from langchain_community.document_loaders import YoutubeLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
# from api_key import GOOGLE_API_KEY
import os
import tempfile
from langchain_community.document_loaders import WebBaseLoader
# GOOGLE_API_KEY = st.secrets.GOOGLE_API_KEY
# llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=GOOGLE_API_KEY)
from langchain_groq import ChatGroq
groq_api_key= st.secrets.GROQ_API_KEY
llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="Llama3-8b-8192")

headers ={
    'groq_api_key' : st.secrets["GROQ_API_KEY"]
}

# llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key="sk-8eTWVikMPM8UywSaztcyrN")

st.title("🤖💬Chat with data")

# File uploader widget
file = st.file_uploader("Upload PDF File", type=["pdf"])
submit = st.checkbox('Submit and chat')

if submit:
   
    # with st.spinner("Creating Vector database..."):
    # st.write('Creating Vector database...')
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file.read())
    file_path = temp_file.name
    temp_file.close()
    
    loader = PyPDFLoader(file_path)
    data = loader.load_and_split()  
    # loader = WebBaseLoader(url)
    # data = loader.load()
    # Split
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1500,
        chunk_overlap = 150
    )
    splits = text_splitter.split_documents(data)

    # word embedding and storing it in Chroma databases
    embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    persist_directory = 'docs/chroma/'

    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=persist_directory
    )


    if 'responses' not in st.session_state:
        st.session_state['responses'] = ["How can I assist you?"]

    if 'requests' not in st.session_state:
        st.session_state['requests'] = []


    # Build prompt
    from langchain.prompts import PromptTemplate
    template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. 
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template,)

    # Run chain
    from langchain.chains import RetrievalQA

    # container for chat history
    response_container = st.container()
    # container for text box
    textcontainer = st.container()


    with textcontainer:
        query = st.chat_input("Query: ", key="input")
        if query:
            with st.spinner("typing..."):

                qa_chain = RetrievalQA.from_chain_type(llm,
                                        retriever=vectordb.as_retriever(),
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})
        
                result = qa_chain({"query": query})
                response = result["result"]

            st.session_state.requests.append(query)
            st.session_state.responses.append(response) 

    with response_container:
        if st.session_state['responses']:

            for i in range(len(st.session_state['responses'])):
                message(st.session_state['responses'][i],key=str(i))
                if i < len(st.session_state['requests']):
                    message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

        
        





