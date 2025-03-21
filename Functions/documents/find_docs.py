import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def load_documents(pkl_file):
    """
    Load documents from a pickle file.
    Expected format: a dictionary where keys are document names and values are text.
    """
    with open(pkl_file, "rb") as f:
        documents = pickle.load(f)
    return documents

def create_faiss_index(documents, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Generate embeddings for the documents and create a FAISS index.
    
    Returns:
        index: FAISS index populated with document embeddings.
        doc_names: List of document names corresponding to the embeddings.
        model: The SentenceTransformer model used for generating embeddings.
    """
    # Extract document names and texts
    doc_names = list(documents.keys())
    doc_texts = list(documents.values())
    
    # Initialize the embedding model
    model = SentenceTransformer(model_name)
    
    # Generate embeddings for each document
    embeddings = model.encode(doc_texts, show_progress_bar=True)
    
    # Ensure embeddings are in a contiguous array of type float32
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # Create a FAISS index using L2 (Euclidean) distance
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(embeddings)
    
    return index, doc_names, model

def search_faiss(query, index, doc_names, model, top_k=3):
    """
    Given a query string, generate its embedding, search the FAISS index,
    and return the top-k most similar documents along with their distance scores.
    
    Returns:
        results: A list of tuples (document name, distance).
    """
    # Encode the query and ensure it's a contiguous float32 array
    query_embedding = model.encode([query])
    query_embedding = np.ascontiguousarray(np.array(query_embedding), dtype=np.float32)
    
    # Perform the FAISS search
    distances, indices = index.search(query_embedding, top_k)
    
    # Collect results, ensuring indices are within bounds
    results = []
    for i in range(top_k):
        doc_idx = indices[0][i]
        if doc_idx < len(doc_names):
            results.append((doc_names[doc_idx], distances[0][i]))
        else:
            results.append(("Unknown", distances[0][i]))
    return results

if __name__ == "__main__":
    # Load documents from the pickle file
    documents = load_documents("documents.pkl")
    print(f"Loaded {len(documents)} documents.")
    
    # Create FAISS index and generate embeddings
    index, doc_names, model = create_faiss_index(documents)
    print(f"Total documents indexed: {index.ntotal}")
    print(f"Index dimension: {index.d}")
    
    # Example query to test the search function
    query = "What are the symptoms of diabetes?"
    results = search_faiss(query, index, doc_names, model, top_k=3)
    
    # Display search results
    print("\nTop search results:")
    for doc, score in results:
        print(f"Document: {doc}, Score: {score:.4f}")
