import os
import gc
import json
import time
import tempfile
import numpy as np
import faiss
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from fastapi.middleware.cors import CORSMiddleware  
from guardrails import Guard

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
# Config
S3_BUCKET_NAME = "medgpt-qa"
# FAISS_FOLDER = "faiss-embedding"
FAISS_INDEX_PATH = "doc/faiss_doc_index_384.bin"
FAISS_METADATA_PATH = "doc/faiss_doc_metadata.json"
BI_ENCODER_LOCAL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# FastAPI app
app = FastAPI()
# Add this block right after creating `app`
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["http://localhost:3000"] during dev for safety
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Loading at startup ------------------

def load_faiss():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(f"FAISS index file not found at {FAISS_INDEX_PATH}")
    if not os.path.exists(FAISS_METADATA_PATH):
        raise FileNotFoundError(f"Metadata file not found at {FAISS_METADATA_PATH}")

    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print("FAISS index and metadata loaded from local files.")
    return index, meta


def get_embedding(text, encoder):
    emb = encoder.encode(text, convert_to_numpy=True)
    if emb.ndim == 1:
        emb = emb[np.newaxis, :]
    return emb.astype("float32")


def rerank_local(query, candidates, cross_encoder, top_n=None):
    pairs = [[query, c["text"]] for c in candidates]
    scores = cross_encoder.predict(pairs)
    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)
    sorted_hits = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    print(f"Reranked {len(candidates)} candidates.")
    return sorted_hits if top_n is None else sorted_hits[:top_n]


def search_faiss(query, faiss_index, metadata, bi_encoder, cross_encoder, top_k=10, rerank_top_k=5):
    q_emb = get_embedding(query, bi_encoder)
    distances, indices = faiss_index.search(q_emb, top_k)

    seen = set()
    results = []
    for i in range(top_k):
        idx = indices[0][i]
        dist = distances[0][i]
        meta = metadata[idx]
        doc_id = meta.get("source")
        chunk_id = meta.get("chunk_id")
        key = (doc_id, chunk_id)
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "rank": len(results) + 1,
            "score": float(dist),
            "source": doc_id,
            "chunk_id": chunk_id,
            "text": meta.get("text")
        })

    return rerank_local(query, results, cross_encoder, top_n=rerank_top_k)


import re

def clean_answer(text):
    # Truncate if the answer ends mid-sentence (no punctuation at end)
    text = text.strip()
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    if sentences:
        # Return all complete sentences that end with proper punctuation
        cleaned = ' '.join([s for s in sentences if re.search(r'[.!?]$', s)])
        if cleaned:
            return cleaned.strip()
    
    # Fallback: return the first complete sentence if nothing matches
    return sentences[0].strip() if sentences else "Answer not available."
SMALL_TALK_RESPONSES = {
    "hello": "Hi there! How can I assist you today?",
    "hi": "Hello! Feel free to ask any medical question.",
    "what can you do": "I can help answer medical questions based on reliable documents.",
    "who are you": "I’m MedGPT, your AI medical assistant.",
    "how are you": "I'm just code, but I'm working perfectly. How can I help you?",
}

def is_small_talk(text):
    normalized = text.lower().strip()
    return next((resp for key, resp in SMALL_TALK_RESPONSES.items() if key in normalized), None)

def generate_answer(question, context, model, tokenizer):
    prompt = (
        "<|system|>You are a helpful and knowledgeable medical assistant.<|end|>\n"
        f"<|user|>Context:\n{context}\n\nQuestion: {question}<|end|>\n"
        f"<|assistant|>The answer is:"
    )
   
    response = generator(
        prompt,
        max_new_tokens=120,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        top_k=40

    )
    parts = response[0]["generated_text"].split("<|assistant|>The answer is: ")
    print("\nAnswer:\n", response[0]["generated_text"])

    if len(parts) > 1:
        raw_answer = parts[1].strip()
        return clean_answer(raw_answer)
    return "Could not extract answer."

# Load models and data once at startup
print("Initializing models and index...")
faiss_index, metadata = load_faiss()
print("loading models.")
bi_encoder = SentenceTransformer(BI_ENCODER_LOCAL)
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
print("Models loaded.")
print("Loading tokenizer and model...")
# Load once at startup
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
print("Loading TinyLlama model...")
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
print("TinyLlama model loaded.")

guard = Guard.from_rail("medical_guardrails.rail")

def generate_guarded_answer(question, context):
    prompt = (
        f"<|system|>You are a helpful and knowledgeable medical assistant.<|end|>\n"
        f"<|user|>Context:\n{context}\n\nQuestion: {question}<|end|>\n"
        f"<|assistant|>The answer is:"
    )

    raw = generator(
        prompt,
        max_new_tokens=120,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        top_k=40
    )[0]["generated_text"]

    print("\nRaw output:\n", raw)
    result = guard.parse(raw, question=question)
    return clean_answer(result.validated_output["answer"])


# ------------------ API Endpoint ------------------

class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: AskRequest):
    start = time.time()
    casual_response = is_small_talk(request.question)
    if casual_response:
        return {
            "question": request.question,
            "answer": casual_response,
            "time_taken": round(time.time() - start, 2)
        }

    results = search_faiss(request.question, faiss_index, metadata, bi_encoder, cross_encoder)
    context_chunks = [res["text"] for res in results]
    context = "\n\n".join(context_chunks[:3])

    # answer = generate_answer(request.question, context, model, tokenizer)
    answer = generate_guarded_answer(request.question, context)
    
    return {
        "question": request.question,
        "answer": answer,
        "time_taken": round(time.time() - start, 2)
    }

# What is Adult Acute Myeloid Leukemia ?
