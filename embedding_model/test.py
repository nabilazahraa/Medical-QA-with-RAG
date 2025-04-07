import boto3
import json
import faiss
import numpy as np
import tempfile

# AWS S3 and SageMaker Configuration
S3_BUCKET_NAME = "medgpt-qa"
FAISS_INDEX_KEY = "qa-embedding/faiss_index_384.bin"
FAISS_METADATA_KEY = "qa-embedding/faiss_metadata.json"
SAGEMAKER_ENDPOINT = "sentence-transformers-all-MiniLM-L6-v2-2025-04-04-10-52-04-531"

# AWS Clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Load FAISS & metadata from S3
def load_faiss():
    """Loads FAISS index and metadata from S3 into Lambda's /tmp/ directory."""
    
    # Download FAISS index from S3
    faiss_index_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_INDEX_KEY)
    faiss_index_data = faiss_index_obj["Body"].read()

    # Write to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(faiss_index_data)
        temp_file.flush()
        temp_file_path = temp_file.name

    # Load FAISS index
    faiss_index = faiss.read_index(temp_file_path)

    # Download FAISS metadata from S3
    faiss_metadata_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_METADATA_KEY)
    faiss_metadata_str = faiss_metadata_obj["Body"].read().decode("utf-8")
    faiss_metadata = json.loads(faiss_metadata_str)

    return faiss_index, faiss_metadata

# Get embedding from SageMaker
def get_embedding(text):
    """Generates an embedding using the SageMaker endpoint and applies mean + max pooling to match FAISS."""
    payload = {"inputs": text}

    # Invoke the SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    # Parse response
    embedding = json.loads(response["Body"].read().decode("utf-8"))
    embedding_array = np.array(embedding).astype("float32")

    # Debugging shape
    print(f"Original embedding shape: {embedding_array.shape}")  # (1, 16, 384)

    # Mean Pooling
    embedding_array = np.mean(embedding_array, axis=1)  # Shape: (1, 384)

  
    # Ensure shape matches FAISS index dimension
    if embedding_array.shape[1] != faiss_index.d:
        raise ValueError(f"Embedding dimension mismatch: Expected {faiss_index.d}, got {embedding_array.shape[1]}")

    return embedding_array  # Shape: (1, 768)


# FAISS search function
def search_faiss(query, top_k=3):
    """Searches FAISS index for the most relevant QA pair based on the query."""
    
    # Generate query embedding using SageMaker
    query_embedding = get_embedding(query)  

    # Check embedding shape before search
    if query_embedding.ndim != 2:
        raise ValueError(f"Query embedding has incorrect shape {query_embedding.shape}, expected (1, d)")

    # Perform FAISS search
    distances, indices = faiss_index.search(query_embedding, top_k)

    results = []
    for i in range(top_k):
        idx = indices[0][i]  # Get index from FAISS
        results.append({
            "question": metadata[idx]["question"],
            "answer": metadata[idx]["answer"],
            "source": metadata[idx]["source"],
            "document_id": metadata[idx]["document_id"],
            "distance": distances[0][i]
        })

    return results

# Load FAISS index and metadata once at startup
faiss_index, metadata = load_faiss()

# Example Query
if __name__ == "__main__":
    query = "What are the symptoms of Adult Acute Lymphoblastic Leukemia"
    results = search_faiss(query, top_k=3)

    # Print results
    for i, res in enumerate(results):
        print(f"Result {i+1}:")
        print(f"Question: {res['question']}")
        print(f"Answer: {res['answer']}")
        print(f"Source: {res['source']}")
        print(f"Document ID: {res['document_id']}")
        print(f"Distance: {res['distance']}")
        print("-" * 50)
