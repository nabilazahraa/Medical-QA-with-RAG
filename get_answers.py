import json
import boto3
import faiss
import numpy as np
import os
import tempfile
import traceback  # Import traceback for detailed error logs


# AWS S3 and SageMaker Configuration
S3_BUCKET_NAME = "med-qa-json"
FAISS_INDEX_KEY = "tmp/faiss_index_384.bin"
FAISS_METADATA_KEY = "tmp/faiss_metadata.json"
SAGEMAKER_ENDPOINT = "sentence-transformer-endpoint"  # Update this with your actual endpoint

# Local file paths inside AWS Lambda
LOCAL_FAISS_INDEX = "/tmp/faiss_index.bin"
LOCAL_METADATA = "/tmp/faiss_metadata.json"

# Initialize AWS Clients
s3 = boto3.client('s3')
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Load FAISS & metadata at startup
def load_faiss():
    """Loads FAISS index and metadata from S3 into Lambda's /tmp/ directory."""
    
    # Download FAISS index from S3
    faiss_index_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_INDEX_KEY)
    faiss_index_data = faiss_index_obj["Body"].read()

    # Write to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(faiss_index_data)
        temp_file.flush()
        temp_file_path = temp_file.name

    # Load FAISS index
    faiss_index = faiss.read_index(temp_file_path)

    # Download FAISS metadata from S3
    faiss_metadata_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=FAISS_METADATA_KEY)
    faiss_metadata_str = faiss_metadata_obj["Body"].read().decode("utf-8")
    faiss_metadata = json.loads(faiss_metadata_str)

    return faiss_index, faiss_metadata

# Get embedding from SageMaker
def get_embedding(text, faiss_index):
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
    mean_pooled = np.mean(embedding_array, axis=1)  # Shape: (1, 384)

    # Concatenate mean and max pooled vectors to get (1, 768)
    embedding_array = mean_pooled

    # Debugging final shape
    print(f"Final embedding shape after pooling: {embedding_array.shape}")  # Should be (1, 768)

    # Ensure shape matches FAISS index dimension
    if embedding_array.shape[1] != faiss_index.d:
        raise ValueError(f"Embedding dimension mismatch: Expected {faiss_index.d}, got {embedding_array.shape[1]}")

    return embedding_array  # Shape: (1, 768)


# FAISS search function
def search_faiss(query, faiss_index, metadata,top_k=3):
    """Searches FAISS index for the most relevant QA pair based on the query."""
    
    # Generate query embedding using SageMaker
    query_embedding = get_embedding(query, faiss_index)  

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


def default_serializer(obj):
    if isinstance(obj, np.float32):  # Check if it's a float32 type
        return float(obj)  # Convert to standard Python float
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


# AWS Lambda Handler
def lambda_handler(event, context):
    """AWS Lambda entry point to handle search queries."""
    try:
        query = event.get("query", "What are the symptoms of leukemia?")
        top_k = int(event.get("top_k", 1))

        print(f"Processing query: {query}")
        # search_faiss
        faiss_index, faiss_metadata = load_faiss()
        if faiss_index is None:
            raise ValueError("FAISS index failed to load properly.")

        # Step 2: Search FAISS for the most relevant answers
        search_results = search_faiss(query,faiss_index,faiss_metadata, top_k)
        # if not search_results:
        #     return {"statusCode": 404, "body": json.dumps({"error": "No results found."})}
       
        return {
            "statusCode": 200,
            "body": json.dumps({
                "query": query,
                "results": search_results
            }, default=default_serializer)
        }
    
    except Exception as e:
        error_message = traceback.format_exc()  # Capture full stack trace
        print(f"Error in Lambda function: {error_message}")  # Print full error details

        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

