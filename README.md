# Real-Time Medical Question-Answering with Retrieval-Augmented Generation

## 🔬 Project Overview

In the healthcare sector, timely access to accurate medical knowledge is essential. This project develops a **real-time medical QA system** that combines **semantic search with reranking**, **large language models**, and **content safety mechanisms** to provide **precise, medically-grounded answers** to user questions.

The system is optimized for disease-related queries and leverages **Retrieval-Augmented Generation (RAG)**, combining fast document search using **FAISS** and **semantic reranking**, followed by **contextual answer generation** using a **Together-hosted LLM** (`Llama-3.3-70B-Instruct-Turbo-Free`). It also integrates **Gemini and Azure Content Safety** to ensure safe and domain-relevant responses.

---

## Dataset

We use structured medical QA datasets such as **MedQuAD** and **CancerGov**, which contain thousands of question-answer pairs across:

- Disease types and diagnosis  
- Treatments and procedures  
- Drug interactions  
- Rare and genetic conditions  

Each document is embedded and stored using **FAISS**, and metadata is preserved for retrieval traceability.

---

## System Pipeline

### 1. Document Indexing & Preprocessing

- Medical XML datasets are parsed and stored in **Amazon S3**
- Each chunk is embedded using a **bi-encoder (`all-MiniLM-L6-v2`)** and indexed with **FAISS**
- Metadata is saved as a parallel JSON file
- The FAISS index and metadata are loaded at runtime

### 2. Real-Time Query Flow

- Users send queries to the **FastAPI backend**
- System detects **small talk** and **non-medical queries** using **Gemini classification**
- For valid medical queries:
  - Bi-encoder retrieves top chunks from FAISS
  - Reranked using **cross-encoder (`ms-marco-MiniLM-L-6-v2`)**
  - Top chunks are passed to Together-hosted **LLM (LLaMA-3.3 70B)** for answer generation
  - Response is **content-validated via Azure Content Safety SDK**
- Clean, domain-relevant answers are returned

### 3. Front-End Integration

- Integrated with a **React.js frontend** supporting real-time interaction
- Response time and source tracking enabled
- Supports loading indicators, statistics, and rerouting for cluster-based workflows

---

## 🔒 Safety and Relevance Filters

To ensure safety and relevance:

- **Gemini** detects and responds to small talk  
- **Gemini** filters out **non-medical questions**  
- **Azure Content Safety** checks final responses against categories:
  - Hate
  - Sexual
  - Self-harm
  - Violence

---

## Evaluation Metrics

| Metric        | Description                                    | Target    |
|---------------|------------------------------------------------|-----------|
| **NDCG**      | Ranking relevance of retrieved content         | ≥ 0.65    |
| **MRR**       | Correctness of top-ranked retrieval            | ≥ 0.70    |
| **BLEU Score**| Fluency and answer overlap with references     | ≥ 0.55    |
| **Latency**   | Sub-second real-time performance               | ≤ 1.0 sec |

---

## Progress Update

| Week  | Task                          | Status     | Notes                                  |
|-------|-------------------------------|------------|----------------------------------------|
| Week 8  | Dataset Parsing & Cleaning     | Complete | MedQuAD and CancerGov parsed           |
| Week 9  | FAISS + Metadata Upload        | Complete | Indexed on AWS S3                      |
| Week 10 | Backend Setup                  | Complete | Search + reranking + LLM API           |
| Week 11 | Gemini + Azure Content Filters | Complete | Integrated for QA safety               |
| Week 11 | Front-End Integration          | Complete | React-based chat interface             |
| Week 12 | Testing                        | Complete | Evaluation metrics                     |

---

## Tech Stack

- **Backend**: FastAPI, FAISS, SentenceTransformers, Transformers  
- **LLMs**: LLaMA-3.3-70B (via Together), Gemini (Google GenAI)  
- **Cloud Services**: Amazon S3, Boto3 
- **Safety Checks**: Azure Content Safety SDK, Gemini prompt-based classifier  
- **Frontend**: React.js  
- **Middleware**: CORS, real-time routing via REST  

---
## Ethical Impact

The development and deployment of a real-time medical question-answering system carry significant ethical responsibilities. Below are key considerations addressed in the design of our system:

### 1. **Accuracy and Reliability**
Providing incorrect or misleading medical advice can have serious consequences. Our system mitigates this risk by:
- Relying exclusively on curated and authoritative datasets (MedQuAD)
- Implementing Retrieval-Augmented Generation (RAG) to ground responses in real documents
- Ensuring hallucination control by instructing the model to answer strictly from context

### 2. **Content Safety**
Given the sensitivity of health-related topics, all generated content is:
- Screened using **Azure Content Safety** to detect hate speech, self-harm, violence, or sexually inappropriate material
- Further filtered for domain relevance using **Gemini’s classification**, ensuring off-topic or casual queries receive appropriate, polite redirection

### 3. **Privacy and Data Handling**
- Our system does **not store user queries** or any identifying data, preserving user privacy
- The system processes text input only for real-time inference without logging or profiling users

### 6. **Transparency**
- The system discloses its sources for each answer to maintain **traceability and trust**
- Users are informed when the system is unable to confidently answer a question due to insufficient context

---
## Evaluation Results

The performance of the medical QA system was evaluated using standard information retrieval and generation metrics. The results are as follows:

| **Metric**         | **Result**     |
|--------------------|----------------|
| **MRR** (Mean Reciprocal Rank) | 0.86           |
| **NDCG** (Normalized Discounted Cumulative Gain) | 0.71           |
| **BLEU Score**     | 0.0082         |
| **Average Latency** (per query) | 4.41 seconds   |

- **High MRR and NDCG** indicate that relevant context chunks were effectively retrieved and ranked at the top positions.
- **Low BLEU** is expected due to the open-ended nature of medical QA where lexical overlap is low; semantic relevance is prioritized over exact phrasing.
- **Latency** remains reasonable for real-time usage despite multi-stage processing (retrieval, reranking, generation, and safety checks).

These results reflect strong retrieval accuracy and a foundation for safe, domain-grounded answer generation.

---
## How to Use This Repository

To run the real-time medical QA system locally:

### 1. Clone the Repository
```bash
git clone https://github.com/nabilazahraa/Medical-QA-with-RAG
cd med-qa-system
```

### 2. Run the Backend
```bash
cd ./Application/Backend
```

(Optional) Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Add your api keys in main.py file:
```
TOGETHER_API_KEY=your_together_api_key
GOOGLE_API_KEY=your_gemini_api_key
AZURE_KEY=your_azure_key
AZURE_ENDPOINT=your_azure_endpoint
```

Run the FastAPI server:
```bash
uvicorn main:app --reload
```

### 3. Run the Frontend
```bash
cd ./Application/Application
npm install
npm run dev
```
--- 

## 📢 Contributors

- **Nabila Zahra**  
- **Hareem Siraj**

---

## 📜 License

This project is open-source under the **MIT License**.
