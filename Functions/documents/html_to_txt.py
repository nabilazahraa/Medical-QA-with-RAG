import boto3
from bs4 import BeautifulSoup

# AWS S3 Configuration
S3_BUCKET_NAME = "med-qa-docs"  # Replace with your bucket name
s3_client = boto3.client("s3")


def list_html_files(bucket_name, prefix="documents/"):
    """List all HTML files in the given S3 bucket, handling pagination properly."""
    html_files = []
    continuation_token = None

    while True:
        # Fetch a batch of objects (with pagination support)
        list_params = {"Bucket": bucket_name, "Prefix": prefix}
        if continuation_token:
            list_params["ContinuationToken"] = continuation_token

        response = s3_client.list_objects_v2(**list_params)

        # Extract HTML file keys (if 'Contents' exists in response)
        if "Contents" in response:
            html_files.extend([obj['Key'] for obj in response["Contents"] if obj["Key"].endswith(".html")])

        # Check if more files are available
        continuation_token = response.get("NextContinuationToken")
        if not continuation_token:
            break  # No more files to fetch

    return html_files

def extract_text_from_html(html_content):
    """Extracts text from an HTML file after removing scripts and styles."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()

    # Extract text
    text = soup.get_text(separator=" ", strip=True)
    return text

def process_and_upload_html_files(bucket_name):
    """Processes all HTML files, extracts text, and uploads cleaned text back to S3."""
    html_files = list_html_files(bucket_name)
  
    for file_key in html_files:
        print(f"Processing: {file_key}")

        # Download file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        html_content = response['Body'].read().decode('utf-8')

        # Extract text
        extracted_text = extract_text_from_html(html_content)

        # Define the new file path in S3 (store in "processed-text/" folder)
        text_file_key = f"processed-text/{file_key.replace('.html', '.txt')}"

        # Upload cleaned text back to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=text_file_key,
            Body=extracted_text.encode("utf-8"),
            ContentType="text/plain"
        )
        print(f"Uploaded: {text_file_key}")

# Run the script
process_and_upload_html_files(S3_BUCKET_NAME)


