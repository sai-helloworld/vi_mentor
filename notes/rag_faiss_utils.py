

# import os
# import hashlib
# from langchain_community.document_loaders import (
#     PyPDFLoader,
#     Docx2txtLoader
# )
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS


# # 🔹 Load embedding model once (important for performance)
# EMBEDDINGS = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )


# # -------------------------------------------------
# # 1️⃣ Detect file type and load document
# # -------------------------------------------------
# def load_document(file_path):
#     ext = os.path.splitext(file_path)[1].lower()

#     if ext == ".pdf":
#         loader = PyPDFLoader(file_path)
#     elif ext == ".docx":
#         loader = Docx2txtLoader(file_path)
#     else:
#         raise ValueError("Unsupported file format. Only PDF and DOCX allowed.")

#     return loader.load()


# # -------------------------------------------------
# # 2️⃣ Generate content hash (for duplicate prevention)
# # -------------------------------------------------
# def generate_file_hash(file_path):
#     hasher = hashlib.md5()

#     with open(file_path, "rb") as f:
#         hasher.update(f.read())

#     return hasher.hexdigest()


# # -------------------------------------------------
# # 3️⃣ Build or update FAISS index
# # -------------------------------------------------
# def build_or_update_faiss_index(file_path: str, vector_dir: str):
#     """
#     Creates or updates FAISS index.
#     Prevents duplicate indexing using file hash.
#     Returns: "indexed" or "duplicate"
#     """

#     os.makedirs(vector_dir, exist_ok=True)

#     file_hash = generate_file_hash(file_path)
#     hash_file_path = os.path.join(vector_dir, "file_hashes.txt")

#     # Check for duplicate
#     if os.path.exists(hash_file_path):
#         with open(hash_file_path, "r") as f:
#             existing_hashes = f.read().splitlines()

#         if file_hash in existing_hashes:
#             return "duplicate"
#     else:
#         existing_hashes = []

#     # Load document
#     docs = load_document(file_path)

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=50
#     )

#     chunks = splitter.split_documents(docs)

#     # Attach metadata
#     for chunk in chunks:
#         chunk.metadata["source_file"] = os.path.basename(file_path)
#         chunk.metadata["file_hash"] = file_hash

#     index_path = os.path.join(vector_dir, "index.faiss")

#     # Load existing or create new
#     if os.path.exists(index_path):
#         vectorstore = FAISS.load_local(
#             vector_dir,
#             EMBEDDINGS,
#             allow_dangerous_deserialization=True
#         )
#         vectorstore.add_documents(chunks)
#     else:
#         vectorstore = FAISS.from_documents(chunks, EMBEDDINGS)

#     vectorstore.save_local(vector_dir)

#     # Save hash
#     with open(hash_file_path, "a") as f:
#         f.write(file_hash + "\n")

#     return "indexed"


# # -------------------------------------------------
# # 4️⃣ Load FAISS safely
# # -------------------------------------------------
# def load_faiss_index(vector_dir):
#     index_path = os.path.join(vector_dir, "index.faiss")

#     if not os.path.exists(index_path):
#         raise FileNotFoundError("Vector index does not exist.")

#     return FAISS.load_local(
#         vector_dir,
#         EMBEDDINGS,
#         allow_dangerous_deserialization=True
#     )


# # -------------------------------------------------
# # 5️⃣ Search with similarity threshold
# # -------------------------------------------------
# def search_with_threshold(vectorstore, query, k=3, threshold=0.8):
#     """
#     FAISS cosine distance:
#     Lower score = better match
#     """

#     docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)

#     if not docs_and_scores:
#         return []

#     best_score = docs_and_scores[0][1]

#     if best_score > threshold:
#         return []

#     return [doc for doc, _ in docs_and_scores]


# import os
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.retrievers import BM25Retriever
# from langchain.retrievers.ensemble import EnsembleRetriever
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

# # 🔹 Initialize Local Hugging Face Embeddings
# # This runs locally and is free. It replaces OpenAIEmbeddings.
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# def build_or_update_faiss_index(file_path, vector_dir):
#     """
#     Extracts text, chunks it, and updates/creates the FAISS index.
#     """
#     # 1. Load the file
#     if file_path.endswith(".pdf"):
#         loader = PyPDFLoader(file_path)
#     elif file_path.endswith(".docx"):
#         loader = Docx2txtLoader(file_path)
#     else:
#         return "unsupported"

#     documents = loader.load()

#     # 2. Split text
#     # Smaller chunks (800) work better with MiniLM embeddings
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=100
#     )
#     docs = text_splitter.split_documents(documents)

#     if not docs:
#         return "empty"

#     # 3. Create/Update Index
#     if not os.path.exists(vector_dir):
#         os.makedirs(vector_dir)
    
#     index_file = os.path.join(vector_dir, "index.faiss")

#     if os.path.exists(index_file):
#         try:
#             # Load existing index
#             vectorstore = FAISS.load_local(
#                 vector_dir, 
#                 embeddings, 
#                 allow_dangerous_deserialization=True
#             )
            
#             # Check for duplicates to prevent bloating
#             existing_sources = {d.metadata.get("source") for d in vectorstore.docstore._dict.values()}
#             if file_path in existing_sources:
#                 return "duplicate"
                
#             vectorstore.add_documents(docs)
#         except Exception as e:
#             # If the index is from OpenAI (incompatible), we overwrite it
#             print(f"Index load failed (likely dimension mismatch): {e}")
#             vectorstore = FAISS.from_documents(docs, embeddings)
#     else:
#         # Create new index
#         vectorstore = FAISS.from_documents(docs, embeddings)

#     # 4. Save
#     vectorstore.save_local(vector_dir)
#     return "success"


# def get_hybrid_retriever(vector_dir):
#     """
#     Loads FAISS index and creates an in-memory BM25 retriever 
#     to combine Semantic (Vector) + Keyword (BM25) search.
#     """
#     if not os.path.exists(os.path.join(vector_dir, "index.faiss")):
#         return None

#     # 1. Load Vector Store (Semantic Search)
#     try:
#         vectorstore = FAISS.load_local(
#             vector_dir, 
#             embeddings, 
#             allow_dangerous_deserialization=True
#         )
#     except Exception:
#         return None

#     faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

#     # 2. Extract Docs to build BM25 (Keyword Search)
#     docstore_docs = list(vectorstore.docstore._dict.values())
    
#     if not docstore_docs:
#         return faiss_retriever 

#     # 3. Create BM25 Retriever
#     bm25_retriever = BM25Retriever.from_documents(docstore_docs)
#     bm25_retriever.k = 4 

#     # 4. Create Ensemble (Hybrid)
#     # 50% Vector (Concepts), 50% Keyword (Exact matches)
#     ensemble_retriever = EnsembleRetriever(
#         retrievers=[faiss_retriever, bm25_retriever],
#         weights=[0.5, 0.5]
#     )

#     return ensemble_retriever







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