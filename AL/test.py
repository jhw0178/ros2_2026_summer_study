import os
import json

from inference_sdk import InferenceHTTPClient


MODEL_ID = "recycle-trnfc/21"

api_key = os.environ.get("ROBOFLOW_API_KEY")

if not api_key:
    raise RuntimeError(
        "ROBOFLOW_API_KEY 환경변수가 설정되지 않았습니다."
    )

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=api_key
)

result = client.infer(
    "test.jpg",
    model_id=MODEL_ID
)

print(json.dumps(result, indent=2, ensure_ascii=False))