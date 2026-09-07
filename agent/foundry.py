import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()


PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("FOUNDRY_MODEL_DEPLOYMENT")


if not PROJECT_ENDPOINT:
    raise ValueError(
        "FOUNDRY_PROJECT_ENDPOINT is missing from .env"
    )

if not MODEL_DEPLOYMENT:
    raise ValueError(
        "FOUNDRY_MODEL_DEPLOYMENT is missing from .env"
    )


credential = DefaultAzureCredential()

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)