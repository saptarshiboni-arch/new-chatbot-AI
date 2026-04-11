import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain

from dotenv import load_dotenv
load_dotenv()

DB_FAISS_PATH = "vectorstore/db_faiss"


def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    db = FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )
    return db




def get_response(user_query):
    try:
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=512,
            api_key=GROQ_API_KEY,
        )

        # ✅ CUSTOM PROMPT (FIXED POSITION)
        CUSTOM_PROMPT_TEMPLATE = """
You are a professional medical assistant.

Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{question}
"""

        custom_prompt = PromptTemplate(
            template=CUSTOM_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )

        # ✅ Chains
        combine_docs_chain = create_stuff_documents_chain(
            llm,
            custom_prompt
        )


        vectorstore = get_vectorstore()

        rag_chain = create_retrieval_chain(
           vectorstore.as_retriever(search_kwargs={'k': 3}),
           combine_docs_chain
        )

        response = rag_chain.invoke({'input': user_query})

        return response["answer"]

    except Exception as e:
        return str(e)