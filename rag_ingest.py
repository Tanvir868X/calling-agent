import os, hashlib, json
from datetime import datetime
from pathlib import Path
from ingest_utils import extract_text_from_file, extract_text_from_url
from pinecone import Pinecone
from pinecone import ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Configs
DATA_DIR = "data"
HASH_DB_PATH = "ingested_hashes.json"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

model = SentenceTransformer("all-MiniLM-L6-v2")

# Init Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Load hash database
if os.path.exists(HASH_DB_PATH):
    with open(HASH_DB_PATH, "r") as f:
        seen_hashes = set(json.load(f))
else:
    seen_hashes = set()

def compute_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def process_files():
    new_hashes = []
    for file in Path(DATA_DIR).glob("*"):
        if file.suffix.lower() in [".pdf", ".txt"]:
            text = extract_text_from_file(file)
        elif file.suffix == ".url":
            with open(file) as f:
                url = f.read().strip()
            text = extract_text_from_url(url)
        else:
            continue

        if not text:
            continue

        content_hash = compute_hash(text)
        if content_hash in seen_hashes:
            print(f"🟡 Skipped (already ingested): {file}")
            continue

        # Embed and upload
        embedding = model.encode(text).tolist()
        index.upsert([(content_hash, embedding, {"source": str(file)})])
        print(f"✅ Ingested: {file}")
        new_hashes.append(content_hash)

    # Save new hashes
    seen_hashes.update(new_hashes)
    with open(HASH_DB_PATH, "w") as f:
        json.dump(list(seen_hashes), f)

if __name__ == "__main__":
    process_files()
