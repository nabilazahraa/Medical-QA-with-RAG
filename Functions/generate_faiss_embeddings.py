import boto3
import json
import numpy as np
import faiss
import os

# AWS Configuration
S3_BUCKET_NAME = "med-qa-json"
FAISS_INDEX_KEY = "tmp/faiss_index_384.bin"
FAISS_METADATA_KEY = "tmp/faiss_metadata.json"
SAGEMAKER_ENDPOINT = "sentence-transformer-endpoint"

# AWS Clients
s3_client = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")

# Function to get embeddings from SageMaker
def get_embedding(text):
    """Generates an embedding using the SageMaker endpoint."""

    print(f"\nGenerating embedding for: {text[:50]}...")  # Print first 50 characters of query

    payload = {"inputs": text}

    # Invoke SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    # Parse response
    embedding = json.loads(response["Body"].read().decode("utf-8"))
    
    print(f"Raw response from SageMaker (first 2 values): {embedding[:2]}...")  # Print first two values to verify

    embedding_array = np.array(embedding).astype("float32")

    # Handle 3D embeddings (sequence_length, embedding_dim)
    if embedding_array.ndim == 3:  
        print(f"Original embedding shape: {embedding_array.shape}")  # Debugging shape
        embedding_array = embedding_array.mean(axis=1)  # Mean pooling

    print(f"Final embedding shape: {embedding_array.shape}")  # Confirm it is (1, 384)


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
index = faiss.IndexFlatIP(dimension)  # Using Inner Product for cosine similarity

# Store metadata for retrieval
metadata = []

local_json_folder = "processed_json"
#create folder


total_files = len([f for f in os.listdir(local_json_folder) if f.endswith(".json")])
processed_files = 0


# Process each JSON file
for json_file in os.listdir(local_json_folder):
    if json_file.endswith(".json"):
        processed_files += 1

        with open(os.path.join(local_json_folder, json_file), "r") as file:
            data = json.load(file)

            for qa in data["qa_pairs"]:
                question = qa["question"]
                answer = qa["answer"]

                # Convert text to embedding using SageMaker
                embedding = get_embedding(question)
                embedding = normalize_embedding(embedding)

                print(f"Adding embedding to FAISS index. Current FAISS size: {index.ntotal}")  # Before adding
                index.add(embedding)
                print(f"FAISS index updated. New size: {index.ntotal}")  # After adding

                # Store metadata
                metadata.append({
                    "question": question,
                    "answer": answer,
                    "source": data["source"],
                    "document_id": data["document_id"]
                })


# Save FAISS index
faiss.write_index(index, "faiss_index_384.bin")
print("\nFAISS index saved successfully!")

# Save metadata for lookup
with open("faiss_metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)

print("FAISS metadata saved successfully!")

