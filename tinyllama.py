from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import time
# Load TinyLLaMA
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
start = time.time()
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Set up the pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)


# question = "What is Adult Acute Myeloid Leukemia ?"
# context = "- Adult acute myeloid leukemia (AML) is a type of cancer in which the bone marrow makes abnormal myeloblasts (a type of white blood cell), red blood cells, or platelets.     - Leukemia may affect red blood cells, white blood cells, and platelets.    - There are different subtypes of AML.     - Smoking, previous chemotherapy treatment, and exposure to radiation may affect the risk of adult AML.    - Signs and symptoms of adult AML include fever, feeling tired, and easy bruising or bleeding.    - Tests that examine the blood and bone marrow are used to detect (find) and diagnose adult AML.    - Certain factors affect prognosis (chance of recovery) and treatment options. Adult acute myeloid leukemia (AML) is a type of cancer in which the bone marrow makes abnormal myeloblasts (a type of white blood cell), red blood cells, or platelets. Adult acute myeloid leukemia (AML) is a cancer of the blood and bone marrow. This type of cancer usually gets worse quickly if it is not treated. It is the most common type of acute leukemia in adults. AML is also called acute myelogenous leukemia, acute myeloblastic leukemia, acute granulocytic leukemia, and acute nonlymphocytic leukemia. Leukemia may affect red blood cells, white blood cells, and platelets. Normally, the bone marrow makes blood stem cells (immature cells) that become mature blood cells over time. A blood stem cell may become a myeloid stem cell or a lymphoid stem cell. A lymphoid stem cell becomes a white blood cell.    A myeloid stem cell becomes one of three types of mature blood cells:         -  Red blood cells that carry oxygen and other substances to all tissues of the body.    - White blood cells that fight infection and disease.    -  Platelets that form blood clots to stop bleeding.         In AML, the myeloid stem cells usually become a type of immature white blood cell called myeloblasts (or myeloid blasts). The myeloblasts in AML are abnormal and do not become healthy white blood cells. Sometimes in AML, too many stem cells become abnormal red blood cells or platelets. These abnormal white blood cells, red blood cells, or platelets are also called leukemia cells or blasts. Leukemia cells can build up in the bone marrow and blood so there is less room for healthy white blood cells, red blood cells, and platelets. When this happens, infection, anemia, or easy bleeding may occur. The leukemia cells can spread outside the blood to other parts of the body, including the central nervous system (brain and spinal cord), skin, and gums.   This summary is about adult AML. See the following PDQ summaries for information about other types of leukemia:         -  Childhood Acute Myeloid Leukemia/Other Myeloid Malignancies Treatment     -  Chronic Myelogenous Leukemia Treatment     -  Adult Acute Lymphoblastic Leukemia Treatment     -  Childhood Acute Lymphoblastic Leukemia Treatment     -  Chronic Lymphocytic Leukemia Treatment     -  Hairy Cell Leukemia Treatment There are different subtypes of AML.                    Most AML subtypes are based on how mature (developed) the cancer cells are at the time of diagnosis and how different they are from normal cells.     Acute promyelocytic leukemia (APL) is a subtype of AML that occurs when parts of two genes stick together. APL usually occurs in middle-aged adults. Signs of APL may include both bleeding and forming blood clots."

question = "What are signs of Childhood Acute Lymphoblastic Leukemia ?"
context = "Key Points - Childhood acute lymphoblastic leukemia (ALL) is a type of cancer in which the bone marrow makes too many immature lymphocytes (a type of white blood cell).    - Leukemia may affect red blood cells, white blood cells, and platelets.    - Past treatment for cancer and certain genetic conditions affect the risk of having childhood ALL.    - Signs of childhood ALL include fever and bruising.    - Tests that examine the blood and bone marrow are used to detect (find) and diagnose childhood ALL.    - Certain factors affect prognosis (chance of recovery) and treatment options. Childhood acute lymphoblastic leukemia (ALL) is a type of cancer in which the bone marrow makes too many immature lymphocytes (a type of white blood cell). Childhood acute lymphoblastic leukemia (also called ALL or acute lymphocytic leukemia) is a cancer of the blood and bone marrow. This type of cancer usually gets worse quickly if it is not treated.     ALL is the most common type of cancer in children. Leukemia may affect red blood cells, white blood cells, and platelets. In a healthy child, the bone marrow makes blood stem cells (immature cells) that become mature blood cells over time. A blood stem cell may become a myeloid stem cell or a lymphoid stem cell.   A myeloid stem cell becomes one of three types of mature blood cells:         -  Red blood cells that carry oxygen and other substances to all tissues of the body.    -  Platelets that form blood clots to stop bleeding.    -  White blood cells that fight infection and disease.         A lymphoid stem cell becomes a lymphoblast cell and then one of three types of lymphocytes (white blood cells):         -  B lymphocytes that make antibodies to help fight infection.    -  T lymphocytes that help B lymphocytes make the antibodies that help fight infection.    -  Natural killer cells that attack cancer cells and viruses.         In a child with ALL, too many stem cells become lymphoblasts, B lymphocytes, or T lymphocytes. The cells do not work like normal lymphocytes and are not able to fight infection very well. These cells are cancer (leukemia) cells. Also, as the number of leukemia cells increases in the blood and bone marrow, there is less room for healthy white blood cells, red blood cells, and platelets. This may lead to infection, anemia, and easy bleeding.   This summary is about acute lymphoblastic leukemia in children, adolescents, and young adults. See the following PDQ summaries for information about other types of leukemia:         -  Childhood Acute Myeloid Leukemia/Other Myeloid Malignancies Treatment     -  Adult Acute Lymphoblastic Leukemia Treatment     -  Chronic Lymphocytic Leukemia Treatment     -  Adult Acute Myeloid Leukemia Treatment     -  Chronic Myelogenous Leukemia Treatment     -  Hairy Cell Leukemia Treatment."
	
prompt = (
    f"<|system|>You are a helpful and knowledgeable medical assistant.<|end|>\n"
    f"<|user|>Context:\n{context}\n\nQuestion: {question}<|end|>\n"
    f"<|assistant|>The answer is:"
)


response = generator(
    prompt,
    max_new_tokens=150,
    temperature=0.7,
    do_sample=True,
    top_p=0.9,
    top_k=40
)

print("\nAnswer:\n", response[0]["generated_text"])
end = time.time()
print("Time taken to generate response: ", end - start, " seconds")

