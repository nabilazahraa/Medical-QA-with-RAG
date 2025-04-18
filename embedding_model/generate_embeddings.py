import boto3
import json

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client("sagemaker-runtime")

# SageMaker Endpoint Name
endpoint_name = "sentence-transformer-endpoint"  # Ensure this is correct

# Function to query SageMaker endpoint for embeddings
def get_sentence_embedding(text):
    try:
        print(f"Sending text for embedding: {text}")

        # Ensure the input is formatted correctly
        payload = {"inputs": [text]}  # Use list format for consistency

        # Invoke SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload),
        )

        # Decode and extract embeddings
        response_body = response["Body"].read().decode("utf-8")
        embedding_result = json.loads(response_body)

        # Handle potential incorrect response format
        if "embedding" in embedding_result:
            return embedding_result["embedding"]
        elif isinstance(embedding_result, list):
            return embedding_result[0]  # Assume first entry contains embeddings
        else:
            print("Unexpected response format:", embedding_result)
            return None

    except Exception as e:
        print(f"Error invoking SageMaker endpoint: {str(e)}")
        return None


# Example Query
query_text = "SageMaker is great for AI!"
embedding = get_sentence_embedding(query_text)

if embedding:
    print("Generated Embedding:", embedding)
else:
    print("Failed to generate embedding.")

