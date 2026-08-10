import os
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient

load_dotenv()

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.environ["ROBOFLOW_API_KEY"],
)

result = client.infer(
    "https://media.roboflow.com/inference/people-walking.jpg",
    model_id="rfdetr-small",
)

print(result)