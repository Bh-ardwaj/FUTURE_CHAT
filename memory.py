# backend/memory.py
import os
import chromadb
from pathlib import Path
import uuid

# ---- Paths ----
BASE_DIR = Path(__file__).parent
MEMORY_DIR = BASE_DIR / "memory"
CHROMA_DIR = MEMORY_DIR / "chroma"

MEMORY_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

# ---- Chroma client (new recommended style) ----
# This avoids the "deprecated configuration" error.
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Create / get collection
collection = client.get_or_create_collection(name="chat_memory")


def save_memory(session_id: str, user_msg: str, ai_msg: str) -> None:
    """
    Save one turn of conversation (user + AI) as a single memory document.
    Example stored text:
        "User: hello\nAI: hi there!"
    """
    try:
        doc = f"User: {user_msg}\nAI: {ai_msg}"
        unique_id = f"{session_id}_{uuid.uuid4().hex}"

        collection.add(
            documents=[doc],
            metadatas=[{"session": session_id}],
            ids=[unique_id],
        )
    except Exception as e:
        # Fail silently so memory issues never crash the app
        print(f"[memory] Error saving memory: {e}")


def retrieve_memory(query: str):
    """
    Retrieve up to 5 most relevant past memory snippets for the given query.
    Returns a list of strings (documents).
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=5,
        )
        docs_lists = results.get("documents", [])
        if not docs_lists:
            return []
        # docs_lists is a list of lists: [ [doc1, doc2, ...] ]
        return docs_lists[0] or []
    except Exception as e:
        print(f"[memory] Error retrieving memory: {e}")
        return []
