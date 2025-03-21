import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker import get_execution_role

# Define AWS region and SageMaker role
region = "eu-north-1"
role = "arn:aws:iam::861276078725:role/service-role/AmazonSageMaker-ExecutionRole-20250309T003483"  # Ensure your IAM role has SageMaker access
s3_model_path = "s3://med-qa-model/model/model.tar.gz"

# Hugging Face Model Environment
environment = {
    "SAGEMAKER_MODEL_SERVER_TIMEOUT": "3600",
    "HF_MODEL_ID": "sentence-transformers/all-MiniLM-L6-v2",
    "HF_TASK": "feature-extraction",
}

# Define model
model = Model(
    image_uri="763104351884.dkr.ecr.eu-north-1.amazonaws.com/huggingface-pytorch-inference:1.10.2-transformers4.17.0-cpu-py38-ubuntu20.04",
    model_data=s3_model_path,
    role=role,
    name="sentence-transformer-miniLM",
    env=environment,
)

# Deploy model to endpoint
predictor = model.deploy(
    instance_type="ml.m5.large",
    initial_instance_count=1,
    endpoint_name="sentence-transformer-endpoint",
)

print(f"Model deployed at endpoint: {predictor.endpoint_name}")
