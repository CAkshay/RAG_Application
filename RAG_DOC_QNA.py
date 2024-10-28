import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

import time
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


os.environ['OPENAI_API_KEY']=(os.getenv('OPENAI_API_KEY'))
os.environ['GROQ_API_KEY']=(os.getenv('GROQ_API_KEY'))

groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

prompt = ChatPromptTemplate.from_template(
    "Answer the question based on the provided context:\n\n{context}\n\nQuestion: {input}"
)

def create_vector_embeddings():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = OpenAIEmbeddings()
        st.session_state.loader = PyPDFDirectoryLoader("research_papers")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)
st.title("RAG with Groq and Mixtral")

user_prompt = st.text_input("Enter your question")

if st.button("Document Embeddings"):
    create_vector_embeddings()
    st.write("Vector Embeddings Created")

if user_prompt:
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    retriver = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriver, document_chain)

    start = time.process_time()
    response = retrieval_chain.invoke({"input": user_prompt})
    print("Response time :", time.process_time() - start)

    st.write(response["answer"])

    with st.expander("Document Similarity Search"):
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------")
