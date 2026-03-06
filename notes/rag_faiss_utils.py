




import os
from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

# -------------------------------------------------------------------------
# ✅ CUSTOM HYBRID RETRIEVER (Replaces EnsembleRetriever)
# -------------------------------------------------------------------------
class HybridRetriever(BaseRetriever):
    """
    A custom retriever that combines Vector Search (FAISS) and Keyword Search (BM25).
    It effectively replaces the missing EnsembleRetriever.
    """
    vector_retriever: BaseRetriever
    keyword_retriever: BaseRetriever

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Get documents from both retrievers and combine them.
        """
        # 1. Get results from Vector Search (Concepts)
        vector_docs = self.vector_retriever.invoke(query)
        
        # 2. Get results from Keyword Search (Exact Words)
        keyword_docs = self.keyword_retriever.invoke(query)

        # 3. Combine and Deduplicate (Weighted 50/50 roughly)
        # We use a dict to remove duplicates by page_content
        combined_docs = {}
        
        # Add keyword docs first (high priority for exact matches)
        for doc in keyword_docs:
            combined_docs[doc.page_content] = doc
            
        # Add vector docs (fill in gaps with conceptual matches)
        for doc in vector_docs:
            if doc.page_content not in combined_docs:
                combined_docs[doc.page_content] = doc
        
        return list(combined_docs.values())

# -------------------------------------------------------------------------

# 🔹 Initialize Local Hugging Face Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_or_update_faiss_index(file_path, vector_dir):
    """
    Extracts text, chunks it, and updates/creates the FAISS index.
    """
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        return "unsupported"

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    docs = text_splitter.split_documents(documents)

    if not docs:
        return "empty"

    if not os.path.exists(vector_dir):
        os.makedirs(vector_dir)
    
    index_file = os.path.join(vector_dir, "index.faiss")

    if os.path.exists(index_file):
        try:
            vectorstore = FAISS.load_local(
                vector_dir, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            # Simple duplicate check
            existing_sources = {d.metadata.get("source") for d in vectorstore.docstore._dict.values()}
            if file_path in existing_sources:
                return "duplicate"
            vectorstore.add_documents(docs)
        except Exception:
            vectorstore = FAISS.from_documents(docs, embeddings)
    else:
        vectorstore = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local(vector_dir)
    return "success"


def get_hybrid_retriever(vector_dir):
    """
    Loads FAISS index and uses our custom HybridRetriever class.
    """
    if not os.path.exists(os.path.join(vector_dir, "index.faiss")):
        return None

    try:
        vectorstore = FAISS.load_local(
            vector_dir, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    except Exception:
        return None

    # 1. Vector Retriever
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # 2. Keyword Retriever (BM25)
    docstore_docs = list(vectorstore.docstore._dict.values())
    if not docstore_docs:
        return faiss_retriever 

    bm25_retriever = BM25Retriever.from_documents(docstore_docs)
    bm25_retriever.k = 4 

    # 3. Use our Custom Class
    return HybridRetriever(
        vector_retriever=faiss_retriever,
        keyword_retriever=bm25_retriever
    )