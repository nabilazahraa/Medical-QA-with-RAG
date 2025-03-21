import boto3
import faiss
import json
import numpy as np
import tempfile
import time
from transformers import AutoTokenizer

# ---------------------- CONFIG ---------------------- #
S3_BUCKET_NAME = "med-qa-docs"
FAISS_FOLDER = "tmp"  # Folder in S3
FAISS_INDEX_KEY = f"{FAISS_FOLDER}/faiss_doc_index_384.bin"
FAISS_METADATA_KEY = f"{FAISS_FOLDER}/faiss_doc_metadata.json"
SAGEMAKER_ENDPOINT = "sentence-transformer-endpoint"
# ---------------------------------------------------- #

# AWS Clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# -------------------- LOAD FAISS & METADATA -------------------- #
def load_faiss_and_metadata():
    """Loads FAISS index and metadata from S3."""
    # Download FAISS index
    with tempfile.NamedTemporaryFile(delete=False) as temp_faiss:
        s3_client.download_file(S3_BUCKET_NAME, FAISS_INDEX_KEY, temp_faiss.name)
        faiss_index = faiss.read_index(temp_faiss.name)

    # Download metadata
    with tempfile.NamedTemporaryFile(delete=False) as temp_meta:
        s3_client.download_file(S3_BUCKET_NAME, FAISS_METADATA_KEY, temp_meta.name)
        with open(temp_meta.name, "r") as f:
            metadata = json.load(f)

    return faiss_index, metadata

# -------------------- EMBEDDING UTILS -------------------- #
def get_query_embedding(query):
    """Generates an embedding for the query using SageMaker."""
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

def normalize(vec):
    """L2-normalize a vector."""
    return vec / np.linalg.norm(vec)

# -------------------- SEARCH FUNCTION -------------------- #
def search_faiss(query, top_k=5, expand_neighbors=True, neighbor_window=1):
    print(f"\n🔍 Searching for query: {query}")
    
    faiss_index, metadata = load_faiss_and_metadata()
    query_embedding = get_query_embedding(query)
    query_embedding = normalize(query_embedding)

    distances, indices = faiss_index.search(query_embedding, top_k)

    # Collect initial hits
    seen = set()
    results = []
    for i in range(top_k):
        idx = indices[0][i]
        dist = distances[0][i]
        meta = metadata[idx]

        doc_id = meta.get("source")
        chunk_id = meta.get("chunk_id")

        # Prevent duplicates
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

        # Expand to nearby chunks
        if expand_neighbors:
            for offset in range(-neighbor_window, neighbor_window + 1):
                neighbor_id = chunk_id + offset
                if offset == 0 or neighbor_id < 0:
                    continue

                for i, m in enumerate(metadata):
                    if m.get("source") == doc_id and m.get("chunk_id") == neighbor_id:
                        key = (doc_id, neighbor_id)
                        if key in seen:
                            continue
                        seen.add(key)
                        results.append({
                            "rank": len(results) + 1,
                            "score": None,  # not FAISS-ranked
                            "source": doc_id,
                            "chunk_id": neighbor_id,
                            "text": m.get("text")
                        })

    return results

# -------------------- EXAMPLE USAGE -------------------- #
if __name__ == "__main__":
    query = "What is Adult Acute Myeloid Leukemia ?"
    top_results = search_faiss(query, top_k=5)

    for result in top_results:
        print(f"\nResult {result['rank']}:")
        print(f"Document: {result['source']}")
        print(f"Chunk ID: {result['chunk_id']}")
        # print(f"Score: {result['score']:.4f}")
        print(f"Text:\n{result['text']}...")  # Limit preview to 500 chars
