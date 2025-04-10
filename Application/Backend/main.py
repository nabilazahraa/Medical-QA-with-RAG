import os
import gc
import json
import time
import tempfile
import numpy as np
import faiss
import boto3

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from fastapi.middleware.cors import CORSMiddleware  # <-- add this

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
# Config
S3_BUCKET_NAME = "medgpt-qa"
FAISS_FOLDER = "faiss-embedding"
FAISS_INDEX_KEY = f"{FAISS_FOLDER}/faiss_doc_index_384.bin"
FAISS_METADATA_KEY = f"{FAISS_FOLDER}/faiss_doc_metadata.json"
BI_ENCODER_LOCAL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# AWS clients
s3_client = boto3.client("s3")

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
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_INDEX_KEY)
    data = obj["Body"].read()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        path = f.name
    index = faiss.read_index(path)
    os.remove(path)

    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_METADATA_KEY)
    meta = json.loads(obj["Body"].read().decode("utf-8"))
    print("FAISS index and metadata loaded.")
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


def generate_answer(question, context, model, tokenizer):
    prompt = (
        "<|system|>You are a helpful and knowledgeable medical assistant.<|end|>\n"
        f"<|user|>Context:\n{context}\n\nQuestion: {question}<|end|>\n"
        f"<|assistant|>The answer is:"
    )

    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    response = generator(
        prompt,
        max_new_tokens=200,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        top_k=40
    )
    parts = response[0]["generated_text"].split("<|assistant|>The answer is: ")
    print("\nAnswer:\n", response[0]["generated_text"])
    return parts[1].strip() if len(parts) > 1 else "Could not extract answer"


# Load models and data once at startup
print("Initializing models and index...")
faiss_index, metadata = load_faiss()
print("loading models.")
bi_encoder = SentenceTransformer(BI_ENCODER_LOCAL)
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
print("Models loaded.")
print("Loading tokenizer and model...")
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
print("Loading TinyLlama model...")
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
print("TinyLlama model loaded.")

# ------------------ API Endpoint ------------------

class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: AskRequest):
    start = time.time()

    results = search_faiss(request.question, faiss_index, metadata, bi_encoder, cross_encoder)
    context_chunks = [res["text"] for res in results]
    context = "\n\n".join(context_chunks[:3])

    answer = generate_answer(request.question, context, model, tokenizer)
    
    return {
        "question": request.question,
        "answer": answer,
        "time_taken": round(time.time() - start, 2)
    }

# What is Adult Acute Myeloid Leukemia ?
