import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import json

torch.set_num_threads(1)

index = faiss.read_index("faiss embeddings/qa/faiss_index_384.bin")
with open("faiss embeddings/qa/faiss_metadata.json", "r") as f:
    metadata = json.load(f)

tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.1")

def get_embedding(text):
    """Converts text into a BioBERT embedding vector."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        output = model(**inputs)
    return output.last_hidden_state[:, 0, :].numpy()

def search_faiss(query, top_k=1):
    """Searches FAISS index for the most relevant QA pair based on the query."""
    query_embedding = get_embedding(query)  
    distances, indices = index.search(query_embedding, top_k) 

    results = []
    for i in range(top_k):
        idx = indices[0][i]  
        results.append({
            "question": metadata[idx]["question"],
            "answer": metadata[idx]["answer"],
            "source": metadata[idx]["source"],
            "document_id": metadata[idx]["document_id"],
            "distance": distances[0][i]
        })

    return results

# Example Query
query = "What are the symptoms of Adult Acute Lymphoblastic Leukemia "
results = search_faiss(query, top_k=5)

# Print Results
for i, res in enumerate(results):
    print(f"Result {i+1}:")
    print(f"Question: {res['question']}")
    print(f"Answer: {res['answer']}")
    print(f"Source: {res['source']}")
    print(f"Document ID: {res['document_id']}")
    print(f"Distance: {res['distance']}")
    print("-" * 50)
#     aws s3 cp lambda_function.zip s3://med-qa-lambda

# aws lambda update-function-code \--function-name get_answers \--s3-bucket med-qa-lambda \--s3-key lambda_function.zip


# aws lambda invoke \--function-name lambda_handler \--payload '{"query": "What are the symptoms of leukemia?", "top_k": 3}' \response.json