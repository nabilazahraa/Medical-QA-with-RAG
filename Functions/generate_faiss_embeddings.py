import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import json
import os

# Load BioBERT tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.1")

def get_embedding(text):
    """Converts text into a BioBERT embedding vector."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        output = model(**inputs)
    return output.last_hidden_state[:, 0, :].numpy()

# Initialize FAISS index for 768-dim BioBERT embeddings
dimension = 768
index = faiss.IndexFlatL2(dimension)

# Store metadata for retrieval
metadata = []

local_json_folder = "processed_json"

# Process each JSON file
for json_file in os.listdir(local_json_folder):
    if json_file.endswith(".json"):
        with open(os.path.join(local_json_folder, json_file), "r") as file:
            data = json.load(file)

            for qa in data["qa_pairs"]:
                question = qa["question"]
                answer = qa["answer"]

                # Convert text to embedding
                embedding = get_embedding(question)
                index.add(embedding)

                # Store metadata
                metadata.append({
                    "question": question,
                    "answer": answer,
                    "source": data["source"],
                    "document_id": data["document_id"]
                })

# Save FAISS index
faiss.write_index(index, "faiss_index.bin")

# Save metadata for lookup
with open("faiss_metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)

print("FAISS embeddings and metadata saved!")
