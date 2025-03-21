import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def search_embeddings(query, index, doc_names, model, top_k=3):
    """
    Given a query string, generate its embedding, search the FAISS index,
    and return the top-k most similar documents with their distances.
    
    Returns:
        results: A list of dictionaries containing 'doc_name' and 'distance' for each hit.
    """
    # Encode the query
    query_embedding = model.encode([query])
    
    # Search the index for the top_k nearest neighbors
    distances, indices = index.search(np.array(query_embedding), top_k)
    
    # Gather results with document names and corresponding distances
    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            "doc_name": doc_names[idx],
            "distance": distances[0][i]
        })
    return results

query = "What are the common symptoms of diabetes?"
index = faiss.read_index("faiss_documents.index")
with open("doc_names.txt", "r") as f:
    doc_names = f.read().splitlines()
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
results = search_embeddings(query, index, doc_names, model, top_k=3)
