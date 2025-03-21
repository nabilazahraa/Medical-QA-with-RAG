import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import boto3

# AWS S3 Configuration
S3_BUCKET_NAME = "med-qa-docs"  # Replace with your bucket name
s3_client = boto3.client("s3")

def list_text_files(bucket_name, prefix="processed-text/documents/"):
    """List all processed text files in S3."""
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(".txt")]

def download_text_from_s3(bucket_name, file_key):
    """Download a text file from S3 and return its content."""
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    print("file_key", file_key)
    return response['Body'].read().decode('utf-8')

# Fetch and store extracted text
text_files = list_text_files(S3_BUCKET_NAME)
documents = {file: download_text_from_s3(S3_BUCKET_NAME, file) for file in text_files}

#save the documents for later use
with open("documents.pkl", "wb") as f:
    pickle.dump(documents, f)


print(f"Fetched {len(documents)} documents from S3.")

