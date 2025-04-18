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
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from azure.core.exceptions import HttpResponseError
import re
import requests
import os
import boto3
import google.generativeai as genai


os.environ["TOGETHER_API_KEY"] = "7a3557cc611a053545585cb7e7107caec0e6740a0d576d6f7b37c51aa5bb0fa2"

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
# Config
S3_BUCKET_NAME = "med-qa-docs"
FAISS_FOLDER = "tmp"
FAISS_INDEX_KEY = "tmp/faiss_doc_index_384.bin"
FAISS_METADATA_KEY = "tmp/faiss_doc_metadata.json"
BI_ENCODER_LOCAL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
import openai

GOOGLE_API_KEY = "AIzaSyB9db9uy39qfJtfJRD2hGGMxpZ5ccFOhZM"

openai.api_base = "https://api.together.xyz/v1"
openai.api_key = os.getenv("TOGETHER_API_KEY")

azure_endpoint = "https://tuco.cognitiveservices.azure.com/"  
azure_key = "EsuxGP8SUN7KyUUZiotqviCgWK32yYzeoFVJEUrt0EMNqEbAUpiCJQQJ99BBACYeBjFXJ3w3AAAHACOGSBj5"

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

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
# ------------------ Loading at startup ------------------
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


def search_faiss(query, faiss_index, metadata, bi_encoder, cross_encoder, top_k=20, rerank_top_k=5):
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


def is_safe_content(text: str, azure_endpoint: str, azure_key: str) -> bool:
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": azure_key
    }
    payload = {
        "text": text,
        "categories": ["hate", "sexual", "self-harm", "violence"]
    }
    response = requests.post(f"{azure_endpoint}contentsafety/text:analyze", json=payload, headers=headers)
    response.raise_for_status()

    results = response.json()
    for category in results.get("categoriesAnalysis", []):
        if category["severity"] >= 2:  # Threshold: 0 (safe) to 4 (very unsafe)
            return False
    return True


def is_medical_answer_gemini(answer_text: str) -> bool:
    prompt = f"""Is the following text related to the medical domain? If it belongs to weather, sports, news, technology, or anything unrelated to health or medicine, respond No. Answer with "Yes" or "No" only.
Text: {answer_text}"""
    response = model.generate_content(prompt)
    response_text = response.text.lower().strip()
    return "yes" in response_text

def is_small_talk_gemini(text: str) -> bool:
    prompt = f"""You are a classifier. Is the following text casual small talk (e.g., greetings, jokes, or general chat) and NOT a serious question?

Respond with "Yes" or "No".

Text: {text}
"""
    try:
        response = model.generate_content(prompt)
        response_text = response.text.lower().strip()
        return "yes" in response_text
    except Exception as e:
        print("Gemini small talk classification error:", e)
        return False
def generate_small_talk_response(text: str) -> str:
    prompt = f"""You are a medical assistant, The user is making casual conversation. Respond politely and naturally, like a friendly medical assistant.

User: {text}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini small talk response error:", e)
        return "I'm here to help with medical or health-related questions!"


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

def generate_answer(question, context, model= "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"):
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", 
             "content":  "You are a helpful and polite assistant. Answer questions strictly based on the retrieved context. "
                    "If the user asks a medical question, respond using only the context provided. Use the context to answer the question. "
                    "If the user asks about weather, sports, news, technology, or anything unrelated to health or medicine, respond with:\n"
                "\"I'm sorry, I can only assist with medical or health-related questions.\"\n\n"
                    "Important: If the context does not provide enough relevant information to answer the question, respond with: "
                    "\"I'm sorry, but the available documents do not contain enough information to answer that.\""},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.7,
        top_p=0.9,
        max_tokens=1024
    )
    raw_answer = response.choices[0].message.content
    print("\nAnswer:\n", raw_answer)
    return raw_answer
 

# Load models and data once at startup
print("Initializing models and index...")
faiss_index, metadata = load_faiss()
print("loading models.")
bi_encoder = SentenceTransformer(BI_ENCODER_LOCAL)
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
print("Models loaded.")
print("Loaded")



def is_safe_content_sdk(text: str, endpoint: str, key: str) -> bool:
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    request = AnalyzeTextOptions(text=text)

    try:
        response = client.analyze_text(request)
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        return False

    for category_analysis in response.categories_analysis:
        if category_analysis.severity >= 2:  # Threshold
            print(f"Content flagged: {category_analysis.category} (Severity: {category_analysis.severity})")
            return False

    return True

# ------------------ API Endpoint ------------------

class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: AskRequest):
    start = time.time()
  
    if is_small_talk_gemini(request.question):
        response = generate_small_talk_response(request.question)
        return {
            "question": request.question,
            "answer": response,
            "time_taken": round(time.time() - start, 2)
        }
    
    if not is_medical_answer_gemini(request.question):
        return {
            "question": request.question,
            "answer": "I can only answer medically-related questions.",
            "time_taken": round(time.time() - start, 2)
        }
    

    results = search_faiss(request.question, faiss_index, metadata, bi_encoder, cross_encoder)
    context_chunks = [res["text"] for res in results]
    context = "\n\n".join(context_chunks[:3])

    answer = generate_answer(request.question, context)

    if not is_safe_content_sdk(answer, azure_endpoint, azure_key):
        return {
            "question": request.question,
            "answer": "Sorry, the content violates safety guidelines.",
            "time_taken": round(time.time() - start, 2)
        }
    

    return {
    "question": request.question,
    "answer": answer,
    "sources": [res["source"] for res in results],  
    "time_taken": round(time.time() - start, 2)
}

# What is Adult Acute Myeloid Leukemia ?
