import os
import xml.etree.ElementTree as ET
import json


input_folder = "datasets/5_NIDDK_QA"
output_folder = "processed_json" 
os.makedirs(output_folder, exist_ok=True)

def parse_xml_to_json(xml_file):
    """Parses an XML file and converts it into structured JSON format."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract metadata
    document_id = root.attrib.get('id', "Unknown")
    source = root.attrib.get('source', "Unknown")
    url = root.attrib.get('url', "")

    focus = root.find("Focus").text if root.find("Focus") is not None else "Unknown"

    # Extract Q/A pairs
    qa_pairs = []
    for qa_pair in root.findall(".//QAPair"):
        question = qa_pair.find("Question").text.strip() if qa_pair.find("Question") is not None else ""
        answer = qa_pair.find("Answer").text.strip() if qa_pair.find("Answer") is not None else ""

        qa_pairs.append({"question": question, "answer": answer})

    # Create JSON structure
    json_data = {
        "document_id": document_id,
        "source": source,
        "url": url,
        "focus": focus,
        "qa_pairs": qa_pairs
    }

    return json_data

# Loop through all XML files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".xml"):
        xml_path = os.path.join(input_folder, filename)
        json_data = parse_xml_to_json(xml_path)

        # Define output JSON file path
        json_filename = filename.replace(".xml", "niddk.json")
        json_path = os.path.join(output_folder, json_filename)

        # Save JSON file
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4)

        print(f"Converted {filename} to {json_filename}")

print("All XML files have been converted to JSON and saved in 'processed_json/'")
