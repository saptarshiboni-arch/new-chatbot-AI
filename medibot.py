import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from dotenv import load_dotenv
load_dotenv()

DB_FAISS_PATH = "vectorstore/db_faiss"

# ✅ GLOBAL CACHE
vectorstore = None


def get_vectorstore():
    global vectorstore

    # ✅ Already loaded
    if vectorstore is not None:
        return vectorstore

    print("Loading vectorstore once...")

    if not os.path.exists(DB_FAISS_PATH):
        print("Vectorstore missing")
        return None

    embedding_model = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )

    vectorstore = FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    print("Vectorstore loaded ✅")
    return vectorstore


def get_response(user_query):
    try:
        # ✅ Load vectorstore (lazy loading)
        vs = get_vectorstore()

        if vs is None:
            return "Vectorstore not found"

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=200,
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        CUSTOM_PROMPT_TEMPLATE = """
You are a professional medical assistant.

Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{input}
"""

        prompt = PromptTemplate(
            template=CUSTOM_PROMPT_TEMPLATE,
            input_variables=["context", "input"]
        )

        combine_docs_chain = create_stuff_documents_chain(
            llm,
            prompt
        )

        rag_chain = create_retrieval_chain(
            vs.as_retriever(search_kwargs={'k': 1}),
            combine_docs_chain
        )

        response = rag_chain.invoke({'input': user_query})

        if isinstance(response, dict):
            return response.get("answer", "No answer")
        else:
            return str(response)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return "Something went wrong. Check terminal."