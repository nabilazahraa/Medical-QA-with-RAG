# import boto3
# import sagemaker
# from sagemaker.model import Model
# from sagemaker import get_execution_role

# # Define AWS region and SageMaker role
# region = "eu-north-1"
# role = "arn:aws:iam::861276078725:role/service-role/AmazonSageMaker-ExecutionRole-20250309T003483"  # Ensure your IAM role has SageMaker access
# s3_model_path = "s3://med-qa-model/model/model.tar.gz"

# # Hugging Face Model Environment
# environment = {
#     "SAGEMAKER_MODEL_SERVER_TIMEOUT": "3600",
#     "HF_MODEL_ID": "sentence-transformers/all-MiniLM-L6-v2 ",

#     "HF_TASK": "feature-extraction",
# }

# # Define model
# model = Model(
#     image_uri="763104351884.dkr.ecr.eu-north-1.amazonaws.com/huggingface-pytorch-inference:1.10.2-transformers4.17.0-cpu-py38-ubuntu20.04",
#     model_data=s3_model_path,
#     role=role,
#     name="sentence-transformer-miniLM",
#     env=environment,
# )

# # Deploy model to endpoint
# predictor = model.deploy(
#     instance_type="ml.m5.large",
#     initial_instance_count=1,
#     endpoint_name="sentence-transformer-endpoint",
# )

# print(f"Model deployed at endpoint: {predictor.endpoint_name}")

#### SAGEMAKER SETUP ####
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel

try:
 role = sagemaker.get_execution_role()
except ValueError:
 iam = boto3.client('iam')
 role = "arn:aws:iam::108782095919:role/model-sagemaker"
 
session = sagemaker.Session()
default_bucket = session.default_bucket()

# Hub Model configuration. <https://huggingface.co/models>
hub = {
  'HF_MODEL_ID':'sentence-transformers/all-MiniLM-L6-v2', # model_id from hf.co/models
  'HF_TASK':'feature-extraction', # NLP task you want to use for predictions
  # 'SM_NUM_GPUS': '1',
}

huggingface_model = HuggingFaceModel(
    env=hub, # configuration for loading model from Hub
    role=role, # iam role with permissions to create an Endpoint
    py_version='py310',
    transformers_version="4.37.0", # transformers version used
    pytorch_version="2.1.0", # pytorch version used
)

embedding_predictor = huggingface_model.deploy(
    endpoint_name=sagemaker.utils.name_from_base("sentence-transformers-all-MiniLM-L6-v2"),
    initial_instance_count=1,
    instance_type="ml.m5.xlarge"
)

embedding_predictor.predict({"inputs": [
        "In un giorno di pioggia, Andrea e Giuliano incontrano Licia per caso.", 
        "Poi Mirko, finita la pioggia, si incontra e si scontra con Licia."
    ]
})