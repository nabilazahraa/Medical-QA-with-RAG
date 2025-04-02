import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker import get_execution_role

# Define AWS region and SageMaker role
region = "us-east-1"
role = "arn:aws:iam::108782095919:role/model-sagemaker"  # Ensure your IAM role has SageMaker access
s3_model_path = "s3://model-embedding/MiniLM/model.tar.gz"

# Hugging Face Model Environment
environment = {
    "SAGEMAKER_MODEL_SERVER_TIMEOUT": "3600",
    "HF_MODEL_ID": "sentence-transformers/all-MiniLM-L6-v2",
    "HF_TASK": "feature-extraction",
}

# Define model
model = Model(
    image_uri="763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04",
    model_data=s3_model_path,
    role=role,
    name="sentence-transformer-miniLM",
    env=environment,
)

# Deploy model to endpoint
predictor = model.deploy(
    instance_type="ml.t2.medium",
    initial_instance_count=1,
    endpoint_name="embedding-endpoint1",
)

if predictor is None:
    print("⚠️ Deployment failed — predictor is None.")
else:
    print(f"✅ Model deployed at endpoint: {predictor.endpoint_name}")

print(f"Model deployed at endpoint: {predictor.endpoint_name}")
