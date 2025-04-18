import boto3
import json
import faiss
import numpy as np
import tempfile
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import time
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"


# AWS S3 and SageMaker Configuration (for bi‑encoder)
S3_BUCKET_NAME = "medgpt-qa"
FAISS_INDEX_KEY = "qa-embedding/faiss_index_384.bin"
FAISS_METADATA_KEY = "qa-embedding/faiss_metadata.json"
BI_ENCODER_ENDPOINT = "sentence-transformers-all-MiniLM-L6-v2-2025-04-04-10-52-04-531"

# Local models for reranking
BI_ENCODER_LOCAL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# AWS Clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Load local models
bi_encoder = SentenceTransformer(BI_ENCODER_LOCAL)
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)

def load_faiss():
    """Loads FAISS index and metadata from S3 into /tmp/."""
    # FAISS index
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_INDEX_KEY)
    data = obj["Body"].read()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        path = f.name
    index = faiss.read_index(path)

    # metadata
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_METADATA_KEY)
    meta = json.loads(obj["Body"].read().decode("utf-8"))

    return index, meta

def get_embedding_local(text):
    """Get bi‑encoder embedding locally."""
    emb = bi_encoder.encode(text, convert_to_numpy=True)
    # emb shape: (d,) or (1, d)
    if emb.ndim == 1:
        emb = emb[np.newaxis, :]
    return emb.astype("float32")  # shape (1, d)

def rerank_local(query, candidates, top_n=None):
    """
    Rerank candidates with a local CrossEncoder.
    candidates: list of dicts with 'answer' field (or full passage).
    Returns the list sorted by descending cross‑encoder score.
    If top_n is provided, returns only the top_n after reranking.
    """
    pairs = [[query, c["answer"]] for c in candidates]
    scores = cross_encoder.predict(pairs)  # array of floats
    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)
    sorted_hits = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return sorted_hits if top_n is None else sorted_hits[:top_n]

def search_faiss(query, top_k=10, rerank_top_k=5, use_local_bi_encoder=False):
    """
    1) Retrieve top_k with FAISS (using either SageMaker or local bi‑encoder),
    2) rerank the top rerank_top_k locally with CrossEncoder,
    3) return final list of length rerank_top_k.
    """
    # 1) embed query
    if use_local_bi_encoder:
        q_emb = get_embedding_local(query)
    else:
        # fallback to SageMaker endpoint
        payload = {"inputs": query}
        resp = sagemaker_runtime.invoke_endpoint(
            EndpointName=BI_ENCODER_ENDPOINT,
            ContentType="application/json",
            Body=json.dumps(payload),
        )
        emb = np.array(json.loads(resp["Body"].read().decode("utf-8")), dtype="float32")
        if emb.ndim == 3:
            emb = emb.mean(axis=1)
        q_emb = emb

    # 2) FAISS search
    distances, indices = faiss_index.search(q_emb, top_k)
    hits = []
    for dist, idx in zip(distances[0], indices[0]):
        m = metadata[idx]
        hits.append({
            "question": m["question"],
            "answer": m["answer"],
            "source": m["source"],
            "document_id": m["document_id"],
            "faiss_distance": float(dist),
        })

    # 3) rerank locally
    final_hits = rerank_local(query, hits[:rerank_top_k], top_n=rerank_top_k)
    return final_hits
def answer(question, context, model, tokenizer):
    
    prompt = (
        "<|system|>You are a helpful and knowledgeable medical assistant.<|end|>\n"
        f"<|user|>Context:\n{context}\n\nQuestion: {question}<|end|>\n"
        f"<|assistant|>The answer is:"
    )


    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    response = generator(
        prompt,
        max_new_tokens=500,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        top_k=40
    )
    # print("\nAnswer:\n", response[0]["generated_text"])
    parts = response[0]["generated_text"].split("<|assistant|>The answer is:")
    if len(parts) > 1:
        return parts[1].strip()
    return "Could not extract answer"
# Load FAISS index & metadata once
faiss_index, metadata = load_faiss()

if __name__ == "__main__":
    q = "What are the symptoms of Adult Acute Lymphoblastic Leukemia"
    # set use_local_bi_encoder=True to avoid SageMaker bi‑encoder calls
    start = time.time()
    results = search_faiss(q, top_k=10, rerank_top_k=5, use_local_bi_encoder=True)
    for i, r in enumerate(results, 1):
        print(f"Rank {i}:")
        print(f"  Q: {r['question']}")
        print(f"  A: {r['answer']}")
        print(f"  Source: {r['source']}")
        print(f"  Doc ID: {r['document_id']}")
        print(f"  FAISS dist: {r['faiss_distance']:.4f}")
        print(f"  Rerank score: {r['rerank_score']:.4f}")
        print("-" * 60)
    print("Loading TinyLLaMA...")
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    
   
    # Build context
    context_chunks = [res["answer"] for res in results]
    context = "\n\n".join(context_chunks[:3])

    # Answer
    res = answer(q, context, model, tokenizer)
    print("\nAnswer:\n", res)
    end = time.time()
    print("Time taken:", end - start, "seconds")
