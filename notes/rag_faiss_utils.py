
# import os
# from langchain_community.document_loaders import (
#     PyPDFLoader,
#     Docx2txtLoader
# )
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS


# def load_document(file_path):
#     """
#     Detect file type and load accordingly.
#     """
#     ext = os.path.splitext(file_path)[1].lower()

#     if ext == ".pdf":
#         loader = PyPDFLoader(file_path)

#     elif ext == ".docx":
#         loader = Docx2txtLoader(file_path)

#     else:
#         raise ValueError("Unsupported file format. Only PDF and DOCX allowed.")

#     return loader.load()


# def build_or_update_faiss_index(file_path: str, vector_dir: str):
#     os.makedirs(vector_dir, exist_ok=True)

#     # Load document dynamically
#     docs = load_document(file_path)

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=50
#     )

#     chunks = splitter.split_documents(docs)

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )

#     index_path = os.path.join(vector_dir, "index.faiss")

#     if os.path.exists(index_path):
#         vectorstore = FAISS.load_local(
#             vector_dir,
#             embeddings,
#             allow_dangerous_deserialization=True
#         )
#         vectorstore.add_documents(chunks)
#     else:
#         vectorstore = FAISS.from_documents(chunks, embeddings)

#     vectorstore.save_local(vector_dir)




import os
import hashlib
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# 🔹 Load embedding model once (important for performance)
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -------------------------------------------------
# 1️⃣ Detect file type and load document
# -------------------------------------------------
def load_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX allowed.")

    return loader.load()


# -------------------------------------------------
# 2️⃣ Generate content hash (for duplicate prevention)
# -------------------------------------------------
def generate_file_hash(file_path):
    hasher = hashlib.md5()

    with open(file_path, "rb") as f:
        hasher.update(f.read())

    return hasher.hexdigest()


# -------------------------------------------------
# 3️⃣ Build or update FAISS index
# -------------------------------------------------
def build_or_update_faiss_index(file_path: str, vector_dir: str):
    """
    Creates or updates FAISS index.
    Prevents duplicate indexing using file hash.
    Returns: "indexed" or "duplicate"
    """

    os.makedirs(vector_dir, exist_ok=True)

    file_hash = generate_file_hash(file_path)
    hash_file_path = os.path.join(vector_dir, "file_hashes.txt")

    # Check for duplicate
    if os.path.exists(hash_file_path):
        with open(hash_file_path, "r") as f:
            existing_hashes = f.read().splitlines()

        if file_hash in existing_hashes:
            return "duplicate"
    else:
        existing_hashes = []

    # Load document
    docs = load_document(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    # Attach metadata
    for chunk in chunks:
        chunk.metadata["source_file"] = os.path.basename(file_path)
        chunk.metadata["file_hash"] = file_hash

    index_path = os.path.join(vector_dir, "index.faiss")

    # Load existing or create new
    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(
            vector_dir,
            EMBEDDINGS,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, EMBEDDINGS)

    vectorstore.save_local(vector_dir)

    # Save hash
    with open(hash_file_path, "a") as f:
        f.write(file_hash + "\n")

    return "indexed"


# -------------------------------------------------
# 4️⃣ Load FAISS safely
# -------------------------------------------------
def load_faiss_index(vector_dir):
    index_path = os.path.join(vector_dir, "index.faiss")

    if not os.path.exists(index_path):
        raise FileNotFoundError("Vector index does not exist.")

    return FAISS.load_local(
        vector_dir,
        EMBEDDINGS,
        allow_dangerous_deserialization=True
    )


# -------------------------------------------------
# 5️⃣ Search with similarity threshold
# -------------------------------------------------
def search_with_threshold(vectorstore, query, k=3, threshold=0.8):
    """
    FAISS cosine distance:
    Lower score = better match
    """

    docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)

    if not docs_and_scores:
        return []

    best_score = docs_and_scores[0][1]

    if best_score > threshold:
        return []

    return [doc for doc, _ in docs_and_scores]
