import os
import chromadb
from chromadb.config import Settings

# Make sure directory exists
MEMORY_DIR = "memory/chroma"
os.makedirs(MEMORY_DIR, exist_ok=True)

# New correct client initialization
client = chromadb.Client(
    Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        persist_directory=MEMORY_DIR
    )
)

# Create or load memory collection
try:
    memory_db = client.get_collection("pewds_memory")
except:
    memory_db = client.create_collection("pewds_memory")


def save_memory(role: str, text: str):
    """Save memory as a document."""
    mem_id = f"id_{memory_db.count()}"
    memory_db.add(
        ids=[mem_id],
        documents=[f"{role}: {text}"],
        metadatas=[{"role": role}]
    )


def retrieve_memory(query: str):
    """Search for related memories."""
    try:
        result = memory_db.query(
            query_texts=[query],
            n_results=3
        )
        if result and "documents" in result:
            return result["documents"][0]
        return []
    except Exception:
        return []
