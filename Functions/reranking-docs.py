import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import gc
import time
import boto3
import json
import faiss
import numpy as np
import tempfile
from sentence_transformers import CrossEncoder, SentenceTransformer 
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# AWS Config
S3_BUCKET_NAME = "medgpt-qa"
FAISS_FOLDER = "faiss-embedding"
FAISS_INDEX_KEY = f"{FAISS_FOLDER}/faiss_doc_index_384.bin"
FAISS_METADATA_KEY = f"{FAISS_FOLDER}/faiss_doc_metadata.json"
BI_ENCODER_LOCAL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
SAGEMAKER_ENDPOINT = "sentence-transformers-all-MiniLM-L6-v2-2025-04-04-10-52-04-531"
# AWS clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

def load_faiss():
    """Loads FAISS index and metadata from S3."""
    # FAISS index
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_INDEX_KEY)
    data = obj["Body"].read()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        path = f.name
    index = faiss.read_index(path)
    os.remove(path)

    # Metadata
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_METADATA_KEY)
    meta = json.loads(obj["Body"].read().decode("utf-8"))
    print("FAISS index and metadata loaded.")
    return index, meta

# def get_embedding_local(text, encoder):
#     emb = encoder.encode(text, convert_to_numpy=True)
#     if emb.ndim == 1:
#         emb = emb[np.newaxis, :]
#     return emb.astype("float32")

def get_embedding(query, encoder):
    """Generates an embedding for the query using SageMaker."""
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    tokenized = tokenizer.encode(query, truncation=True, max_length=512, add_special_tokens=True)
    truncated_text = tokenizer.decode(tokenized, skip_special_tokens=True)

    payload = {"inputs": truncated_text}
    time.sleep(1)  # Optional delay to avoid rate limits

    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    embedding = json.loads(response["Body"].read().decode("utf-8"))
    embedding_array = np.array(embedding).astype("float32")

    if embedding_array.ndim == 3:
        embedding_array = embedding_array.mean(axis=1)

    return embedding_array

def rerank_local(query, candidates, cross_encoder, top_n=None):
    pairs = [[query, c["text"]] for c in candidates]
    scores = cross_encoder.predict(pairs)
    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)
    sorted_hits = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
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

    # return response[0]["generated_text"]

if __name__ == "__main__":
    start = time.time()
    question = "How many people are affected by achondrogenesis ?"

    # Load FAISS index + metadata
    faiss_index, metadata = load_faiss()

    # Load reranking models
    bi_encoder = SentenceTransformer(BI_ENCODER_LOCAL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)

    # Search + rerank
    results = search_faiss(question, faiss_index, metadata, bi_encoder, cross_encoder)

    # # Cleanup: Delete and free memory before TinyLLaMA
    # del cross_encoder
    # del bi_encoder
    # gc.collect()

    # Load TinyLLaMA model AFTER cleanup
    print("Loading TinyLLaMA...")
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    
   
    # Build context
    context_chunks = [res["text"] for res in results]
    context = "\n\n".join(context_chunks[:3])

    # Answer
    res = answer(question, context, model, tokenizer)
    print("\nAnswer:\n", res)
    end = time.time()
    print("Time taken:", end - start, "seconds")
    # Cleanup: Delete and free memory after answer
    # del model
    # del tokenizer
    # gc.collect()
    # # Cleanup: Delete and free memory after answer
    # del results
    # del faiss_index
    # del metadata
    # gc.collect()
    # # Cleanup: Delete and free memory after answer
    # del context_chunks
    # del context
