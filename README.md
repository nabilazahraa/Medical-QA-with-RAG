# Real-Time Medical Question-Answering with Retrieval-Augmented Generation

## 🔬 Project Overview

In the healthcare sector, timely access to accurate medical knowledge is essential. This project develops a **real-time medical QA system** that combines **semantic search with reranking**, **large language models**, and **content safety mechanisms** to provide **precise, medically-grounded answers** to user questions.

The system is optimized for disease-related queries and leverages **Retrieval-Augmented Generation (RAG)**, combining fast document search using **FAISS** and **semantic reranking**, followed by **contextual answer generation** using a **Together-hosted LLM** (`Llama-3.3-70B-Instruct-Turbo-Free`). It also integrates **Gemini and Azure Content Safety** to ensure safe and domain-relevant responses.

---

## 📚 Dataset

We use structured medical QA datasets such as **MedQuAD** and **CancerGov**, which contain thousands of question-answer pairs across:

- Disease types and diagnosis  
- Treatments and procedures  
- Drug interactions  
- Rare and genetic conditions  

Each document is embedded and stored using **FAISS**, and metadata is preserved for retrieval traceability.

---

## ⚙️ System Pipeline

### 1️⃣ Document Indexing & Preprocessing

- Medical XML datasets are parsed and stored in **Amazon S3**
- Each chunk is embedded using a **bi-encoder (`all-MiniLM-L6-v2`)** and indexed with **FAISS**
- Metadata is saved as a parallel JSON file
- The FAISS index and metadata are loaded at runtime

### 2️⃣ Real-Time Query Flow

- Users send queries to the **FastAPI backend**
- System detects **small talk** and **non-medical queries** using **Gemini classification**
- For valid medical queries:
  - Bi-encoder retrieves top chunks from FAISS
  - Reranked using **cross-encoder (`ms-marco-MiniLM-L-6-v2`)**
  - Top chunks are passed to Together-hosted **LLM (LLaMA-3.3 70B)** for answer generation
  - Response is **content-validated via Azure Content Safety SDK**
- Clean, domain-relevant answers are returned

### 3️⃣ Front-End Integration

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

## 📊 Evaluation Metrics

| Metric        | Description                                    | Target    |
|---------------|------------------------------------------------|-----------|
| **NDCG**      | Ranking relevance of retrieved content         | ≥ 0.65    |
| **MRR**       | Correctness of top-ranked retrieval            | ≥ 0.70    |
| **BLEU Score**| Fluency and answer overlap with references     | ≥ 0.55    |
| **Latency**   | Sub-second real-time performance               | ≤ 1.0 sec |

---

## 📅 Progress Tracker

| Week  | Task                          | Status     | Notes                                  |
|-------|-------------------------------|------------|----------------------------------------|
| Week 8  | Dataset Parsing & Cleaning     | ✅ Complete | MedQuAD and CancerGov parsed           |
| Week 9  | FAISS + Metadata Upload        | ✅ Complete | Indexed on AWS S3                      |
| Week 10 | Backend Setup                  | ✅ Complete | Search + reranking + LLM API           |
| Week 11 | Gemini + Azure Content Filters | ✅ Complete | Integrated for QA safety               |
| Week 11 | Front-End Integration          | ✅ Complete | React-based chat interface             |
| Week 12 | Testing                        | ✅ Complete | Evaluation metrics                     |

---

## 🛠 Tech Stack

- **Backend**: FastAPI, FAISS, SentenceTransformers, Transformers  
- **LLMs**: LLaMA-3.3-70B (via Together), Gemini (Google GenAI)  
- **Cloud Services**: Amazon S3, Boto3 
- **Safety Checks**: Azure Content Safety SDK, Gemini prompt-based classifier  
- **Frontend**: React.js  
- **Middleware**: CORS, real-time routing via REST  

---

## 📢 Contributors

- **Nabila Zahra**  
- **Hareem Siraj**

---

## 📜 License

This project is open-source under the **MIT License**.
