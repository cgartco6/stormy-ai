import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
from config.settings import MEMORY_DIR, ENABLE_MEMORY

class Memory:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.enabled = ENABLE_MEMORY
        if not self.enabled:
            return
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=MEMORY_DIR
        ))
        self.collection = self.client.get_or_create_collection(
            name=f"user_{user_id}",
            metadata={"hnsw:space": "cosine"}
        )

    def add_interaction(self, user_input, stormy_response, mood=None, location=None):
        if not self.enabled:
            return
        timestamp = datetime.now().isoformat()
        metadata = {
            "timestamp": timestamp,
            "user_mood": mood or "unknown",
            "location": location or "unknown"
        }
        text = f"User: {user_input}\nStormy: {stormy_response}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[f"interaction_{timestamp}"]
        )

    def add_fact(self, key, value, category="user_preference"):
        if not self.enabled:
            return
        fact_id = f"fact_{key}_{datetime.now().isoformat()}"
        self.collection.add(
            documents=[f"{key}: {value}"],
            metadatas=[{"type": "fact", "category": category, "key": key}],
            ids=[fact_id]
        )

    def recall(self, query, n_results=5):
        if not self.enabled:
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

    def get_user_preferences(self):
        if not self.enabled:
            return {}
        results = self.collection.query(
            query_texts=[""],
            n_results=100,
            where={"type": "fact"}
        )
        facts = {}
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            if meta.get('type') == 'fact':
                key = meta.get('key')
                if key and doc.startswith(f"{key}:"):
                    value = doc.split(":", 1)[1].strip()
                    facts[key] = value
        return facts
