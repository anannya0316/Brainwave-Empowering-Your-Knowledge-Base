import streamlit as st
from streamlit_chat import message
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import tempfile
import os

st.title("🤖💬 Chat with Data")

tab1, tab2 = st.tabs(["Chat with PDF", "Chat with Website"])

with tab1:
    groq_api_key = st.secrets["GROQ_API_KEY"]
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

    # File uploader widget
    file = st.file_uploader("Upload PDF File", type=["pdf"])
    submit = st.checkbox('Submit and chat')

    if submit and file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.read())
                file_path = temp_file.name

            loader = PyPDFLoader(file_path)
            data = loader.load_and_split()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=150
            )
            splits = text_splitter.split_documents(data)

            # Word embedding and storing it in FAISS vector store
            embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            vectordb = FAISS.from_documents(splits, embedding)

            if 'responses' not in st.session_state:
                st.session_state['responses'] = ["How can I assist you?"]
            if 'requests' not in st.session_state:
                st.session_state['requests'] = []

            template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. 
            {context}
            Question: {question}
            Helpful Answer:"""
            QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)

            # Container for chat history
            response_container = st.container()
            # Container for text box
            textcontainer = st.container()

            with textcontainer:
                query = st.chat_input("Query: ", key="input")
                if query:
                    with st.spinner("Typing..."):
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
                        message(st.session_state['responses'][i], key=str(i))
                        if i < len(st.session_state['requests']):
                            message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')

        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
    elif submit:
        st.warning("Please upload a PDF file.")


with tab2:
    groq_api_key = st.secrets["GROQ_API_KEY"]
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

    # File uploader widget
    url = st.text_input("Enter website URL:")
    submit = st.checkbox('Submitt and chat')

    if submit and url is not None:
        try:

            loader = WebBaseLoader(url)
            data = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=150
            )
            splits = text_splitter.split_documents(data)

            # Word embedding and storing it in FAISS vector store
            embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            vectordb = FAISS.from_documents(splits, embedding)

            if 'responses' not in st.session_state:
                st.session_state['responses'] = ["How can I assist you?"]
            if 'requests' not in st.session_state:
                st.session_state['requests'] = []

            template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. 
            {context}
            Question: {question}
            Helpful Answer:"""
            QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)

            # Container for chat history
            response_container = st.container()
            # Container for text box
            textcontainer = st.container()

            with textcontainer:
                query = st.chat_input("Query: ", key="input2")
                if query:
                    with st.spinner("Typing..."):
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
                        message(st.session_state['responses'][i], key=str(i))
                        if i < len(st.session_state['requests']):
                            message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')

        except Exception as e:
            st.error(f"An error occurred: {e}")

    elif submit:
        st.warning("Please Enter url first.")
