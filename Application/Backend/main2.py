# import os
# import gc
# import json
# import time
# import tempfile
# import numpy as np
# import faiss

# from fastapi import FastAPI
# from pydantic import BaseModel
# from sentence_transformers import CrossEncoder, SentenceTransformer
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# from fastapi.middleware.cors import CORSMiddleware  # <-- add this

# os.environ["OMP_NUM_THREADS"] = "1"
# os.environ["MKL_NUM_THREADS"] = "1"
# # Config
# S3_BUCKET_NAME = "medgpt-qa"
# # FAISS_FOLDER = "faiss-embedding"
# FAISS_INDEX_PATH= "qa/faiss_index_384.bin"
# FAISS_METADATA_PATH = "qa/faiss_metadata.json"
# BI_ENCODER_LOCAL = "sentence-transformers/all-MiniLM-L6-v2"
# CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# # FastAPI app
# app = FastAPI()
# # Add this block right after creating `app`
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Replace with ["http://localhost:3000"] during dev for safety
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------ Loading at startup ------------------

# def load_faiss():
#     if not os.path.exists(FAISS_INDEX_PATH):
#         raise FileNotFoundError(f"FAISS index file not found at {FAISS_INDEX_PATH}")
#     if not os.path.exists(FAISS_METADATA_PATH):
#         raise FileNotFoundError(f"Metadata file not found at {FAISS_METADATA_PATH}")

#     index = faiss.read_index(FAISS_INDEX_PATH)
#     with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
#         meta = json.load(f)

#     print("FAISS index and metadata loaded from local files.")
#     return index, meta


# def get_embedding(text, encoder):
#     emb = encoder.encode(text, convert_to_numpy=True)
#     if emb.ndim == 1:
#         emb = emb[np.newaxis, :]
#     return emb.astype("float32")


# def rerank_local(query, candidates, top_n=None):
#     """
#     Rerank candidates with a local CrossEncoder.
#     candidates: list of dicts with 'answer' field (or full passage).
#     Returns the list sorted by descending cross‑encoder score.
#     If top_n is provided, returns only the top_n after reranking.
#     """
#     pairs = [[query, c["answer"]] for c in candidates]
#     scores = cross_encoder.predict(pairs)  # array of floats
#     for c, score in zip(candidates, scores):
#         c["rerank_score"] = float(score)
#     sorted_hits = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
#     return sorted_hits if top_n is None else sorted_hits[:top_n]

# def search_faiss(query, top_k=10, rerank_top_k=5):
#     """
#     1) Retrieve top_k with FAISS (using either SageMaker or local bi‑encoder),
#     2) rerank the top rerank_top_k locally with CrossEncoder,
#     3) return final list of length rerank_top_k.
#     """
#     # 1) embed query
#     # if use_local_bi_encoder:
#     q_emb = get_embedding(query, bi_encoder)
#     # else:
#     #     # fallback to SageMaker endpoint
#     #     payload = {"inputs": query}
#     #     resp = sagemaker_runtime.invoke_endpoint(
#     #         EndpointName=BI_ENCODER_ENDPOINT,
#     #         ContentType="application/json",
#     #         Body=json.dumps(payload),
#     #     )
#     #     emb = np.array(json.loads(resp["Body"].read().decode("utf-8")), dtype="float32")
#     #     if emb.ndim == 3:
#     #         emb = emb.mean(axis=1)
#     #     q_emb = emb

#     # 2) FAISS search
#     distances, indices = faiss_index.search(q_emb, top_k)
#     hits = []
#     for dist, idx in zip(distances[0], indices[0]):
#         m = metadata[idx]
#         hits.append({
#             "question": m["question"],
#             "answer": m["answer"],
#             "source": m["source"],
#             "document_id": m["document_id"],
#             "faiss_distance": float(dist),
#         })

#     # 3) rerank locally
#     final_hits = rerank_local(query, hits[:rerank_top_k], top_n=rerank_top_k)
#     return final_hits

# def generate_answer(question, context, model, tokenizer):
#     prompt = (
#         "<|system|>You are a helpful and knowledgeable medical assistant.<|end|>\n"
#         f"<|user|>Context:\n{context}\n\nQuestion: {question}<|end|>\n"
#         f"<|assistant|>The answer is:"
#     )

#     generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
#     response = generator(
#         prompt,
#         max_new_tokens=120,
#         # temperature=0.7,
#         # do_sample=True,
#         # top_p=0.9,
#         # top_k=40
#     )
#     parts = response[0]["generated_text"].split("<|assistant|>The answer is: ")
#     print("\nAnswer:\n", response[0]["generated_text"])
#     return parts[1].strip() if len(parts) > 1 else "Could not extract answer"


# # Load models and data once at startup
# print("Initializing models and index...")
# faiss_index, metadata = load_faiss()
# print("loading models.")
# bi_encoder = SentenceTransformer(BI_ENCODER_LOCAL)
# cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
# print("Models loaded.")
# print("Loading tokenizer and model...")
# tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
# print("Loading TinyLlama model...")
# model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
# print("TinyLlama model loaded.")

# # ------------------ API Endpoint ------------------

# class AskRequest(BaseModel):
#     question: str


# @app.post("/ask")
# def ask(request: AskRequest):
#     start = time.time()

#     results = search_faiss(request.question)
#     context_chunks = [res["answer"] for res in results]
#     context = "\n\n".join(context_chunks[:3])

#     answer = generate_answer(request.question, context, model, tokenizer)
    
#     return {
#         "question": request.question,
#         "answer": answer,
#         "time_taken": round(time.time() - start, 2)
#     }

# # What is Adult Acute Myeloid Leukemia ?
