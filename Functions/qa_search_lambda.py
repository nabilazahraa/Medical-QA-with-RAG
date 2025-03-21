import boto3
import json
import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# AWS S3 Configuration
S3_BUCKET_NAME = "med-qa-json"
FAISS_INDEX_KEY = "tmp/faiss_index.bin"
METADATA_KEY = "tmp/faiss_metadata.json"

# Local file paths inside Lambda
LOCAL_FAISS_INDEX = "/tmp/faiss_index.bin"
LOCAL_METADATA = "/tmp/faiss_metadata.json"

# Initialize S3 client
s3_client = boto3.client("s3")

# Load FAISS & metadata at startup
def load_faiss_from_s3():
    """Download FAISS index & metadata from S3 and load them."""
    s3_client.download_file(S3_BUCKET_NAME, FAISS_INDEX_KEY, LOCAL_FAISS_INDEX)
    s3_client.download_file(S3_BUCKET_NAME, METADATA_KEY, LOCAL_METADATA)

    global index, metadata
    index = faiss.read_index(LOCAL_FAISS_INDEX)
    
    with open(LOCAL_METADATA, "r") as f:
        metadata = json.load(f)
    
    print(f"FAISS index loaded with {index.ntotal} embeddings.")
    print(f"Metadata loaded with {len(metadata)} entries.")

# Load BioBERT Model
BIOBERT_MODEL = "dmis-lab/biobert-base-cased-v1.1"
tokenizer = AutoTokenizer.from_pretrained(BIOBERT_MODEL)
model = AutoModel.from_pretrained(BIOBERT_MODEL)

def get_embedding(text):
    """Convert text to BioBERT embedding."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        output = model(**inputs)
    return np.ascontiguousarray(output.last_hidden_state[:, 0, :].squeeze().numpy(), dtype=np.float32)

def search_faiss(query, top_k=3):
    """Search FAISS index for the most relevant QA pairs."""
    query_embedding = get_embedding(query)
    query_embedding = np.expand_dims(query_embedding, axis=0)

    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in range(top_k):
        idx = indices[0][i]
        if idx >= len(metadata) or idx < 0:
            print(f"Warning: FAISS index {idx} out of range.")
            continue
        
        results.append({
            "question": metadata[idx]["question"],
            "answer": metadata[idx]["answer"],
            "source": metadata[idx]["source"],
            "document_id": metadata[idx]["document_id"],
            "distance": distances[0][i]
        })

    return results

def lambda_handler(event, context):
    """AWS Lambda entry point."""
    query = event.get("query", "What are the symptoms of leukemia?")
    top_k = int(event.get("top_k", 3))

    search_results = search_faiss(query, top_k)

    return {
        "query": query,
        "results": search_results
    }

# Load FAISS when Lambda container starts
load_faiss_from_s3()
