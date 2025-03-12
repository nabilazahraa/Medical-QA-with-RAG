# Real-Time Medical Question-Answering with Retrieval-Augmented Generation on AWS

## 🔬 Project Overview

In the healthcare sector, timely access to accurate medical knowledge is critical for informed decision-making. This project aims to develop a **real-time medical document Question-Answering (QA) system** leveraging AWS cloud services for **scalable, low-latency information retrieval**. 

By integrating a **vector database for document embedding retrieval** and a **large language model (BioBERT) for contextual Q&A**, we aim to provide **precise and instant responses** to medical queries. Our system will focus on **disease-related questions**, ensuring rapid and accurate access to key healthcare information.

---

## 📚 Dataset

We will utilize **MedQuAD**, a publicly available medical Q&A dataset containing **12,723 QA pairs** sourced from reputable organizations such as **NIH, NCI, and the Genetic and Rare Diseases Information Center**. 

The dataset covers:
- Disease diagnosis
- Treatments
- Drug interactions
- Genetic conditions

To enhance **domain-specific medical comprehension**, we will fine-tune **BioBERT** on this dataset for improved accuracy in medical Q/A.

---

## 🚀 Proposed Pipeline and AWS Implementation

The system consists of **three key phases**:

### 1️⃣ **Document Ingestion and Preprocessing**
- Medical documents and XML files are stored in **Amazon S3** for structured storage.
- **XML parsing** extracts questions, answers, and URLs.
- External medical documents from dataset URLs are fetched and preprocessed.
- Text is converted into **embeddings using FAISS** for efficient retrieval.

### 2️⃣ **Real-Time Query Processing**
- Users submit **medical questions** via the front end, triggering **AWS API Gateway and AWS Lambda**.
- The **Lambda function searches FAISS** for relevant question-answer pairs.
- If no exact answer is found, the system retrieves **medical documents from S3 or external sources**.
- The retrieved text is passed to **AWS SageMaker-hosted BioBERT**, which generates **an accurate, context-aware response** before returning it to the user.

### 3️⃣ **Front-End and Demo**
- The system is **tested via Postman**.
- A **React-based front end** allows users to interact with the system.
- **API Gateway ensures real-time performance validation**.
- A **live demo** will showcase:
  - Query processing flow
  - Retrieval from MedQuAD and external documents
  - LLM-generated answers
  - Performance metrics tracking

---

## 📊 Performance Metrics & Evaluation

| Metric  | Description | Baseline/Target |
|---------|------------|----------------|
| **NDCG (Normalized Discounted Cumulative Gain)** | Measures the ranking relevance of retrieved medical documents | **0.65** |
| **MRR (Mean Reciprocal Rank)** | Evaluates correctness of top-ranked answers | **0.7** |
| **Latency** | Goal is to achieve a sub-second response time | **≤ 1.0 s** |
| **BLEU Score** | Assesses answer fluency and accuracy | **Target: 0.55+** |

---

<!-- ## ⏳ Proposed Schedule and Milestones

| Week | Phase | Milestone |
|------|-------|-----------|
| **1-3**  | Phase 1 | Initial Setup and Dataset Integration |
| **4-6**  | Phase 2 | Query Processing and API Development |
| **7-9**  | Phase 3 | Front-End Development and Real-Time Testing |
| **10-12** | Phase 4 | Performance Evaluation, Optimization | -->

---

## 📅 Progress Updates

| Week | Task | Status | Notes |
|------|------|--------|-------|
| Week 8  | Initial Dataset Integration | Complete | Cleaning and preprocessing MedQuAD dataset |
| Week 9  | FAISS/Pinecone Setup | Completed | Successfully indexed dataset embeddings |
| Week 10 | Extract text from documents | In Progress | Extracting structured text from urls |
| Week 10 | Query Processing API | In Progress | Implementing Lambda-based retrieval |
<!-- | Week 1 | Front-End Development | 🚧 Pending | React UI implementation in pipeline | -->

*(The table will be updated as progress is made)*

---

## 🛠 Tech Stack

- **Cloud Services**: AWS (S3, API Gateway, Lambda, SageMaker)
- **Databases**: FAISS (Vector Database)
- **Model**: BioBERT (Fine-tuned on MedQuAD)
- **Frontend**: React.js
- **Backend**: AWS Lambda with API Gateway
- **Testing & Deployment**: Postman, AWS CloudWatch

---

## 📢 Contributors

👩‍💻 **Nabila Zahra** (nz07162)  
👩‍💻 **Hareem Siraj** (hs07488)

---

## 📜 License

This project is open-source under the **MIT License**. 

---

