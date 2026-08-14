
import os
import cv2
import time
from concurrent.futures import ThreadPoolExecutor

from inference import get_model
import supervision as sv


# 모델 설정
PET_MODEL_ID = "plastic-bottles-ip5yb-uziag-hg1ll/1"
CAN_MODEL_ID = "can-or-can-not-pwbv4/2"
PAPER_MODEL_ID = "siddhants-workspace-3y7tn/crumpled-paper-detection-neac2-2-rfdetr-seg-small-t1"

PET_THRESHOLD = 0.80
CAN_THRESHOLD = 0.80
PAPER_THRESHOLD = 0.60

WIDTH = 640
HEIGHT = 480
FPS = 30


# API Key
api_key = os.environ.get("ROBOFLOW_API_KEY")

if not api_key:
    raise RuntimeError(
        "ROBOFLOW_API_KEY가 설정되지 않았습니다.\n"
        "터미널에서 다음을 실행하세요:\n"
        "export ROBOFLOW_API_KEY='YOUR_API_KEY'"
    )


# 모델 로딩
print("모델 로딩 중...")

pet_model = get_model(
    model_id=PET_MODEL_ID,
    api_key=api_key
)

can_model = get_model(
    model_id=CAN_MODEL_ID,
    api_key=api_key
)

paper_model = get_model(
    model_id=PAPER_MODEL_ID,
    api_key=api_key
)

print("모델 로딩 완료")


# 카메라
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    raise RuntimeError("카메라를 열 수 없습니다.")


def convert_result(result, threshold):
    detections = sv.Detections.from_inference(result)
    predictions = []

    if len(detections) == 0:
        return predictions

    class_names = detections.data.get("class_name")

    for i in range(len(detections)):
        if detections.confidence is not None:
            confidence = float(detections.confidence[i])
        else:
            confidence = 0.0

        if confidence < threshold:
            continue

        x1, y1, x2, y2 = detections.xyxy[i]

        if class_names is not None:
            class_name = str(class_names[i])
        else:
            class_name = str(detections.class_id[i])

        predictions.append({
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2),
            "confidence": confidence,
            "class": class_name
        })

    return predictions


def infer_model(model, frame, threshold):
    try:
        result = model.infer(frame)[0]
        return convert_result(result, threshold)
    except Exception as e:
        print("Inference 오류:", e)
        return []


executor = ThreadPoolExecutor(max_workers=1)

future = None

pet_predictions = []
can_predictions = []
paper_predictions = []


def run_inference(frame):
    # 세 모델을 순차적으로 실행
    pet = infer_model(
        pet_model,
        frame,
        PET_THRESHOLD
    )

    can = infer_model(
        can_model,
        frame,
        CAN_THRESHOLD
    )

    paper = infer_model(
        paper_model,
        frame,
        PAPER_THRESHOLD
    )

    return pet, can, paper


def draw_predictions(frame, predictions, color, prefix):
    for p in predictions:
        x1 = p["x1"]
        y1 = p["y1"]
        x2 = p["x2"]
        y2 = p["y2"]

        label = (
            f"{prefix}{p['class']} "
            f"{p['confidence']:.2f}"
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )


print()
print("Waste Detection Start")
print("PET   :", PET_MODEL_ID)
print("CAN   :", CAN_MODEL_ID)
print("PAPER :", PAPER_MODEL_ID)
print("Camera:", WIDTH, "x", HEIGHT)
print("q : 종료")


fps = 0.0
last_time = time.perf_counter()


while True:
    ret, frame = cap.read()

    if not ret:
        print("카메라 프레임 읽기 실패")
        break

    # 이전 inference가 끝났으면 결과 가져오기
    if future is not None and future.done():
        try:
            pet_predictions, can_predictions, paper_predictions = (
                future.result()
            )
        except Exception as e:
            print("Inference 오류:", e)

        future = None

    # 새로운 inference 시작
    if future is None:
        inference_frame = frame.copy()

        future = executor.submit(
            run_inference,
            inference_frame
        )

    # 결과 표시
    draw_predictions(
        frame,
        pet_predictions,
        (255, 0, 0),
        "[PET] "
    )

    draw_predictions(
        frame,
        can_predictions,
        (0, 255, 0),
        "[CAN] "
    )

    draw_predictions(
        frame,
        paper_predictions,
        (0, 0, 255),
        "[PAPER] "
    )

    # FPS
    current_time = time.perf_counter()
    elapsed = current_time - last_time
    last_time = current_time

    if elapsed > 0:
        instant_fps = 1.0 / elapsed

        if fps == 0:
            fps = instant_fps
        else:
            fps = fps * 0.9 + instant_fps * 0.1

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    total = (
        len(pet_predictions)
        + len(can_predictions)
        + len(paper_predictions)
    )

    cv2.putText(
        frame,
        f"Objects: {total}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Waste Detection",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


cap.release()

executor.shutdown(
    wait=False,
    cancel_futures=True
)

cv2.destroyAllWindows()

print("프로그램 종료")

