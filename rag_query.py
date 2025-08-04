import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# --- Environment Variables ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Initialize Pinecone and Gemini ---
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

genai.configure(api_key=GOOGLE_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")

# --- Embed model ---
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# --- RAG Retrieval Function ---
def get_gemini_answer(query, top_k=5):
    # Step 1: Embed the question
    query_embedding = embed_model.encode(query).tolist()

    # Step 2: Retrieve similar documents
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    # Step 3: Build context from retrieved text
    context_chunks = [match['metadata']['text'] for match in results['matches']]
    context_text = "\n\n".join(context_chunks)

    # Step 4: Ask Gemini
    prompt = f"""You are a helpful medical support assistant. Use the following context to answer the question.

Context:
{context_text}

Question:
{query}

Answer:"""

    response = gemini.generate_content(prompt)
    return response.text
