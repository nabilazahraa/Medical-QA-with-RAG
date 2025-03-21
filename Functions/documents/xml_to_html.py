import boto3
import requests
import xml.etree.ElementTree as ET
import time

# AWS S3 Configuration
SOURCE_BUCKET = "med-qa-xml"  # Bucket containing XML files
DEST_BUCKET = "med-qa-docs"  # Bucket for storing downloaded documents
s3_client = boto3.client("s3")

# List of folders to process
FOLDERS = ["1_CancerGov_QA", "3_GHR_QA", "5_NIDDK_QA"]  # Update with your actual folder names

def list_all_xml_files():
    """ List all XML files from multiple folders in the S3 bucket """
    xml_files = []
    
    for folder_name in FOLDERS:
        continuation_token = None  # For pagination

        while True:
            if continuation_token:
                response = s3_client.list_objects_v2(
                    Bucket=SOURCE_BUCKET, Prefix=f"{folder_name}/", ContinuationToken=continuation_token
                )
            else:
                response = s3_client.list_objects_v2(Bucket=SOURCE_BUCKET, Prefix=f"{folder_name}/")

            # Extract XML file keys (paths) that end with ".xml"
            for obj in response.get("Contents", []):
                if obj["Key"].endswith(".xml"):
                    xml_files.append(obj["Key"])

            # Check if there are more objects to retrieve (pagination)
            continuation_token = response.get("NextContinuationToken")
            if not continuation_token:
                break

    return xml_files

def extract_urls_from_xml(xml_content):
    """ Extract document ID, source, and URLs from XML """
    root = ET.fromstring(xml_content)

    doc_id = root.get("id")
    source = root.get("source")
    url = root.get("url")

    if not url:
        print("WARNING: No URL attribute found in <Document> tag!")

    print(f"Extracted: doc_id={doc_id}, source={source}, url={url}")  # Debugging
    return [(doc_id, source, url)] if url else []

def fetch_and_store_document(file_key):
    """ Fetches a single document from an XML file and stores it in S3 """
    print(f"Processing XML file: {file_key}")

    try:
        # Download XML file from S3
        xml_obj = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=file_key)
        xml_content = xml_obj["Body"].read().decode("utf-8")

        # Extract URLs from the XML file
        urls = extract_urls_from_xml(xml_content)

        for doc_id, source, url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    safe_source = "".join(c if c.isalnum() or c in "-_" else "_" for c in source) if source else "unknown"
                    output_file_key = f"documents/{safe_source}_{doc_id}.html"
                    s3_client.put_object(Bucket=DEST_BUCKET, Key=output_file_key, Body=response.content)
                    print(f"Uploaded {output_file_key} to S3")
                else:
                    print(f"Failed to fetch document {doc_id} from {url}")
            except Exception as e:
                print(f"Error fetching {url}: {e}")

    except Exception as e:
        print(f"Error processing {file_key}: {e}")

def process_all_xml_files(batch_size=10, delay=2):
    """ Process all XML files from multiple folders in batches """
    xml_files = list_all_xml_files()

    if not xml_files:
        print("No XML files found in the specified folders.")
        return

    print(f"Total {len(xml_files)} XML files found. Processing in batches of {batch_size}...")

    for i in range(0, len(xml_files), batch_size):
        batch = xml_files[i:i + batch_size]
        for file_key in batch:
            fetch_and_store_document(file_key)
        print(f"Processed {i + len(batch)} / {len(xml_files)} files")
        time.sleep(delay)  # Small delay to avoid throttling

# Run the script to process all three folders
if __name__ == "__main__":
    process_all_xml_files(batch_size=10, delay=2)  # Adjust batch size if needed

