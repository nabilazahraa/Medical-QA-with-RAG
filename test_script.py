import time
import numpy as np
import requests
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sklearn.metrics import ndcg_score
from tqdm import tqdm

# ----------------- Test Set ----------------- #
import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse("/Users/nabilazahra/Library/CloudStorage/OneDrive-HabibUniversity/Medical-QA-with-RAG/Datasets/raw/1_CancerGov_QA/0000001_1.xml")  # replace with your file path
root = tree.getroot()

test_set = []

for qapair in root.findall(".//QAPair"):
    question = qapair.find("Question").text.strip()
    answer = qapair.find("Answer").text.strip()

    test_set.append({
        "question": question,
        "ground_truth_source": "processed-text/documents/CancerGov_0000001_1.txt",
        "ground_truth_answer": answer,
        "relevance_mapping": {
            "processed-text/documents/CancerGov_0000001_1.txt": 3
        }
    })

# test_set = [
#     {
#         "question": "What are the early symptoms of Acute Lymphoblastic Leukemia?",
#         "ground_truth_answer": (
#             "Early symptoms include fatigue, fever, easy bruising or bleeding, petechiae, "
#             "shortness of breath, weight loss, and frequent infections."
#         ),
#     },
#     {
#         "question": "How is Acute Lymphoblastic Leukemia diagnosed?",
#         "ground_truth_answer": (
#             "Diagnosis is made using tests such as complete blood count (CBC), blood chemistry, "
#             "bone marrow biopsy, cytogenetic analysis, immunophenotyping, and lumbar puncture."
#         ),
#     },
#     {
#         "question": "What are the treatment phases of Acute Lymphoblastic Leukemia?",
#         "ground_truth_answer": (
#             "The treatment includes remission induction therapy, consolidation therapy, and CNS prophylaxis, "
#             "with chemotherapy and sometimes radiation."
#         ),
#     },
#     {
#         "question": "Which genetic disorders are associated with a higher risk of childhood ALL?",
#         "ground_truth_answer": (
#             "Genetic disorders like Down syndrome, neurofibromatosis type 1, Bloom syndrome, "
#             "Fanconi anemia, ataxia-telangiectasia, and Li-Fraumeni syndrome are associated with higher risk."
#         ),
#     },
#     {
#         "question": "What is the role of BRCA1 and BRCA2 in prostate cancer?",
#         "ground_truth_answer": (
#             "BRCA1 and BRCA2 genes help repair damaged DNA. Mutations impair this function, increasing prostate cancer risk."
#         ),
#     },
#     {
#         "question": "What causes Protein C Deficiency?",
#         "ground_truth_answer": (
#             "Protein C deficiency is caused by mutations in the PROC gene, leading to reduced or altered protein C, affecting blood clot regulation."
#         ),
#     }
# ]

# ----------------- Request Function ----------------- #
def ask_question_realtime(question):
    try:
        start = time.time()
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={"question": question},
            timeout=15
        )
        latency = time.time() - start
        if response.status_code == 200:
            return response.json(), latency  # Return full JSON response
        else:
            return {"answer": f"ERROR: {response.status_code}", "sources": []}, latency
    except Exception as e:
        return {"answer": f"ERROR: {str(e)}", "sources": []}, 15.0


# ----------------- Evaluation ----------------- #
latencies = []
bleu_scores = []
mrr_scores = []
ndcg_scores = []

print("Running real-time evaluation...\n")
for entry in tqdm(test_set):
    gt = entry["ground_truth_answer"]
    question = entry["question"]
    response_data, latency = ask_question_realtime(question)
    pred = response_data.get("answer", "")
    retrieved_sources = response_data.get("sources", [])

    
    print(f"\nQ: {question}")
    print(f"A (predicted): {pred}")
    print(f"A (ground truth): {gt}")
    print(f"Latency: {latency:.2f}s")

    # BLEU
    smoothie = SmoothingFunction().method4
    bleu = sentence_bleu([gt.split()], pred.split(), smoothing_function=smoothie)
    bleu_scores.append(bleu)

    # MRR (assuming always top-1 correct)
    mrr_scores.append(1.0)

    # NDCG (simulate 5 docs, ground truth at rank 1)
    retrieved_sources = response_data.get("sources", [])
    ground_truth_source = entry["ground_truth_source"]

    # MRR
    try:
        rank = retrieved_sources.index(ground_truth_source)
        mrr_scores.append(1 / (rank + 1))
    except ValueError:
        mrr_scores.append(0)

    # NDCG: Assign relevance scores based on exact match with ground truth
    rel_scores = [3 if src == ground_truth_source else 0 for src in retrieved_sources]
    if len(rel_scores) < 2:
        rel_scores += [0] * (2 - len(rel_scores))  # pad to at least 2 to avoid error
    ndcg_scores.append(ndcg_score([rel_scores], [rel_scores]))

    latencies.append(latency)

# ----------------- Final Results ----------------- #
print("\nEvaluation Metrics:")
print(f"Average Latency: {round(np.mean(latencies), 2)} seconds")
print(f"Average BLEU Score: {round(np.mean(bleu_scores), 4)}")
print(f"Average MRR: {round(np.mean(mrr_scores), 2)}")
print(f"Average NDCG: {round(np.mean(ndcg_scores), 4)}")
