import boto3
import json
import numpy as np
import faiss
import os
import time
import tempfile
from transformers import AutoTokenizer

# AWS Configuration
S3_BUCKET_NAME = "med-qa-docs"
S3_DOCUMENTS_FOLDER = "processed-text/documents"  # Updated folder path in S3
FAISS_INDEX_KEY = "faiss_doc_index_384.bin"
FAISS_METADATA_KEY = "faiss_doc_metadata.json"
SAGEMAKER_ENDPOINT = "sentence-transformer-endpoint"

# AWS Clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Load tokenizer for chunking text
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")  # Adjust model if needed

# Function to split text into ≤512-token chunks
def split_text_into_chunks(text, max_tokens=512):
    tokens = tokenizer.encode(text, truncation=False)  # Tokenize without truncation
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]  # Split into max 512 tokens each
    return [tokenizer.decode(chunk) for chunk in chunks]  # Convert back to text

# Function to get embeddings from SageMaker
def get_embedding(text):
    """Generates an embedding using the SageMaker endpoint."""
    start_time = time.time()  # Start timing

    print(f"\nGenerating embedding for: {text[:50]}...")  # Print first 50 characters

    tokenized_text = tokenizer.encode(text, truncation=True, max_length=512, add_special_tokens=True)
    truncated_text = tokenizer.decode(tokenized_text, skip_special_tokens=True)

    payload = {"inputs": truncated_text}

    # Invoke SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    # Parse response
    embedding = json.loads(response["Body"].read().decode("utf-8"))
    
    print(f"Raw response from SageMaker (first 2 values): {embedding[:2]}...")  # Debugging output

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

# **Step 1: List `.txt` files in S3 Bucket**
print(f"Listing files in S3 bucket: {S3_BUCKET_NAME}/{S3_DOCUMENTS_FOLDER}")

s3_objects = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_DOCUMENTS_FOLDER)
if "Contents" not in s3_objects:
    print(f"No documents found in S3 path: {S3_DOCUMENTS_FOLDER}")
else:
    total_files = len(s3_objects["Contents"])
    print(f"Found {total_files} documents in S3.")

    # **Step 2: Process Each Document**
    for obj in s3_objects["Contents"]:
        s3_key = obj["Key"]
        if not s3_key.endswith(".txt"):
            continue  # Skip non-text files

        print(f"\nProcessing file: {s3_key}")

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
                "text": chunk,  # Store chunk text for retrieval
                "source": s3_key,
                "chunk_id": chunk_index,
                "type": "document_chunk"
            })

        print(f"Finished processing document: {s3_key} (Total Chunks: {len(text_chunks)})")

# **Step 6: Save FAISS Index and Metadata**
faiss.write_index(index, "faiss_doc_index_384.bin")
print("\nFAISS index saved successfully!")

# Save metadata for lookup
with open("faiss_doc_metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)

print("FAISS metadata saved successfully!")

# **Step 7: Upload FAISS Index and Metadata to S3**
# s3_client.upload_file("faiss_index_384.bin", S3_BUCKET_NAME, FAISS_INDEX_KEY)
# s3_client.upload_file("faiss_metadata.json", S3_BUCKET_NAME, FAISS_METADATA_KEY)

print(f"\nFAISS index and metadata uploaded to S3: {S3_BUCKET_NAME}")

