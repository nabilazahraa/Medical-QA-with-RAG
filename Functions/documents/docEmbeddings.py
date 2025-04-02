import boto3
import json
import numpy as np
import faiss
import os
import time
import tempfile
import gc
from transformers import AutoTokenizer

# AWS Configuration
S3_BUCKET_NAME = "med-qa-docs"
S3_DOCUMENTS_FOLDER = "processed-text/documents"
FAISS_INDEX_KEY = "tmp/faiss_doc_index_384.bin"
FAISS_METADATA_KEY = "tmp/faiss_doc_metadata.json"
SAGEMAKER_ENDPOINT = "sentence-transformer-endpoint"

# # AWS Clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Load tokenizer for chunking text
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Function to list all `.txt` files from S3 using pagination
def list_all_s3_files(bucket_name, prefix):
    """Fetches all files from S3 using pagination to avoid 1000-object limit."""
    files = []
    continuation_token = None

    while True:
        list_params = {"Bucket": bucket_name, "Prefix": prefix}
        if continuation_token:
            list_params["ContinuationToken"] = continuation_token

        response = s3_client.list_objects_v2(**list_params)

        if "Contents" in response:
            files.extend(response["Contents"])

        # Check if more pages exist
        if response.get("IsTruncated"):  # More files available
            continuation_token = response["NextContinuationToken"]
        else:
            break  # No more pages

    return [obj for obj in files if obj["Key"].endswith(".txt")]  # Return only .txt files

# Function to split text into ≤512-token chunks
def split_text_into_chunks(text, max_tokens=512):
    tokens = tokenizer.encode(text, truncation=False, add_special_tokens=False)  # Tokenize without truncation
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]  # Split into 512-token chunks
    return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]  # Convert back to text

# Function to get embeddings from SageMaker
def get_embedding(text):
    """Generates an embedding using the SageMaker endpoint with enforced 512-token max."""
    start_time = time.time()

    # **Ensure truncation before sending to SageMaker**
    tokenized_text = tokenizer.encode(text, truncation=True, max_length=512, add_special_tokens=True)
    truncated_text = tokenizer.decode(tokenized_text, skip_special_tokens=True)

    print(f"\nGenerating embedding for: {truncated_text[:50]}...")  # Print first 50 characters

    payload = {"inputs": truncated_text}

    # Introduce a small delay to avoid rate limits
    time.sleep(1)

    # Invoke SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    # Parse response
    embedding = json.loads(response["Body"].read().decode("utf-8"))

    # print(f"Raw response from SageMaker (first 2 values): {embedding[:2]}...")  # Debugging output

    embedding_array = np.array(embedding).astype("float32")

    # Handle 3D embeddings (sequence_length, embedding_dim)
    if embedding_array.ndim == 3:
        print(f"Original embedding shape: {embedding_array.shape}")  # Debugging
        embedding_array = embedding_array.mean(axis=1)  # Mean pooling

    print(f"Final embedding shape: {embedding_array.shape}")  # Confirm (1, 384)

    elapsed_time = time.time() - start_time
    print(f"Time taken for embedding: {elapsed_time:.2f} seconds")

    return embedding_array  # Should be (1, 384)

# Function to normalize embeddings
def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding)
    if norm == 0:
        print("Warning: Zero norm detected in embedding!")
        return embedding
    return embedding / norm

# Initialize FAISS index for 384D embeddings
dimension = 384
index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity

# Store metadata for retrieval
metadata = []

# Track total execution time
overall_start_time = time.time()

# **Step 1: List ALL `.txt` files in S3 Bucket**
print(f"Fetching all files in S3 bucket: {S3_BUCKET_NAME}/{S3_DOCUMENTS_FOLDER}")
s3_files = list_all_s3_files(S3_BUCKET_NAME, S3_DOCUMENTS_FOLDER)
total_files = len(s3_files)
print(f"✅ Found {total_files} documents in S3.")

# **Step 2: Process Each Document**
for obj_index, obj in enumerate(s3_files):
    s3_key = obj["Key"]
    
    print(f"\nProcessing file {obj_index + 1}/{total_files}: {s3_key}")

    # **Step 3: Download the file from S3**
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        s3_client.download_file(S3_BUCKET_NAME, s3_key, temp_file.name)
    
    # Read the document text
    with open(temp_file.name, "r", encoding="utf-8") as file:
        document_text = file.read()

    # **Step 4: Split text into smaller chunks (max 512 tokens)**
    text_chunks = split_text_into_chunks(document_text)

    chunk_embeddings = []
    for chunk_index, chunk in enumerate(text_chunks):
        print(f"\nProcessing chunk {chunk_index + 1}/{len(text_chunks)} of document: {s3_key}")

        # **Step 5: Generate embedding for each chunk**
        embedding = get_embedding(chunk)
        embedding = normalize_embedding(embedding)

        # Store embedding in FAISS
        index.add(embedding)
        chunk_embeddings.append(embedding)

        # Store metadata for this chunk
        metadata.append({
            "text": chunk,
            "source": s3_key,
            "chunk_id": chunk_index,
            "type": "document_chunk"
        })

    print(f"✅ Finished processing document: {s3_key} (Total Chunks: {len(text_chunks)})")

    # **Step 6: Save FAISS Index Periodically to Reduce Memory Usage**
    if obj_index % 10 == 0:  # Save FAISS every 10 documents
        print("\n💾 Saving FAISS index to prevent high memory usage...")
        faiss.write_index(index, "faiss_doc_index_384.bin")
        with open("faiss_doc_metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
        gc.collect()  # Free memory

# **Step 7: Final Save & Upload**
faiss.write_index(index, "faiss_doc_index_384.bin")
with open("faiss_doc_metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)

s3_client.upload_file("faiss_doc_index_384.bin", S3_BUCKET_NAME, FAISS_INDEX_KEY)
s3_client.upload_file("faiss_doc_metadata.json", S3_BUCKET_NAME, FAISS_METADATA_KEY)

print(f"\n✅ FAISS index and metadata uploaded to S3: {S3_BUCKET_NAME}")

# # Track total execution time
# overall_elapsed_time = time.time() - overall_start_time
# print(f"\n⏳ Total execution time: {overall_elapsed_time:.2f} seconds.")
