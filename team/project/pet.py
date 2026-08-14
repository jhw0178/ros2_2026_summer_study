
import os
import cv2
import time

from inference import get_model
import supervision as sv


# =========================================================
# 설정
# =========================================================

MODEL_ID = "plastic-bottles-ip5yb-uziag-hg1ll/1"

CONFIDENCE_THRESHOLD = 0.80

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30


# =========================================================
# API Key
# =========================================================

api_key = os.environ.get("ROBOFLOW_API_KEY")

if not api_key:
    raise RuntimeError(
        "ROBOFLOW_API_KEY가 설정되지 않았습니다.\n\n"
        "터미널에서 다음 명령을 실행하세요:\n"
        "export ROBOFLOW_API_KEY='YOUR_API_KEY'\n\n"
        "그리고 다시 실행하세요."
    )

print("====================================")
print("Plastic Bottle Detection")
print("====================================")
print()
print("API Key: 설정됨")
print(f"Model: {MODEL_ID}")
print()


# =========================================================
# 모델 로딩
# =========================================================

print("모델 로딩 중...")

model = get_model(
    model_id=MODEL_ID,
    api_key=api_key,
)

print("모델 로딩 완료")
print()


# =========================================================
# Camera
# =========================================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_V4L2
)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT
)

cap.set(
    cv2.CAP_PROP_FPS,
    CAMERA_FPS
)

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG")
)

cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)


if not cap.isOpened():
    raise RuntimeError(
        "카메라를 열 수 없습니다."
    )


# =========================================================
# FPS 계산용 변수
# =========================================================

prev_time = time.perf_counter()

fps = 0.0

frame_count = 0


# =========================================================
# Detection 결과 변환
# =========================================================

def convert_result(
    result,
    threshold
):

    detections = (
        sv.Detections.from_inference(
            result
        )
    )

    predictions = []

    if len(detections) == 0:
        return predictions

    class_names = (
        detections.data.get(
            "class_name"
        )
    )

    for i in range(
        len(detections)
    ):

        # ---------------------------------------------
        # Confidence
        # ---------------------------------------------

        if (
            detections.confidence
            is not None
        ):

            confidence = float(
                detections.confidence[i]
            )

        else:

            confidence = 0.0


        # ---------------------------------------------
        # Threshold
        # ---------------------------------------------

        if confidence < threshold:
            continue


        # ---------------------------------------------
        # Bounding Box
        # ---------------------------------------------

        x1, y1, x2, y2 = (
            detections.xyxy[i]
        )


        # ---------------------------------------------
        # Class
        # ---------------------------------------------

        if class_names is not None:

            class_name = str(
                class_names[i]
            )

        else:

            class_name = str(
                detections.class_id[i]
            )


        predictions.append(
            {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),

                "confidence": confidence,

                "class": class_name,
            }
        )


    return predictions


# =========================================================
# Inference
# =========================================================

def run_inference(frame):

    try:

        result = (
            model.infer(
                frame
            )[0]
        )

        return convert_result(
            result,
            CONFIDENCE_THRESHOLD
        )

    except Exception as e:

        print(
            "Inference 오류:",
            e
        )

        return []


# =========================================================
# Bounding Box
# =========================================================

def draw_predictions(
    frame,
    predictions
):

    for p in predictions:

        x1 = p["x1"]
        y1 = p["y1"]
        x2 = p["x2"]
        y2 = p["y2"]

        class_name = p["class"]

        confidence = (
            p["confidence"]
        )


        # ---------------------------------------------
        # Bounding Box
        # ---------------------------------------------

        cv2.rectangle(
            frame,

            (x1, y1),
            (x2, y2),

            (255, 0, 0),

            2,
        )


        # ---------------------------------------------
        # Label
        # ---------------------------------------------

        label = (
            f"{class_name} "
            f"{confidence:.2f}"
        )


        cv2.putText(
            frame,

            label,

            (
                x1,
                max(
                    y1 - 10,
                    25
                )
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.60,

            (255, 0, 0),

            2,
        )


# =========================================================
# 시작
# =========================================================

print("====================================")
print("Plastic Bottle Detection Start")
print()
print(f"Model : {MODEL_ID}")
print(
    f"Camera: "
    f"{CAMERA_WIDTH} x "
    f"{CAMERA_HEIGHT} / "
    f"{CAMERA_FPS} FPS"
)
print()
print("q : 종료")
print("====================================")


# =========================================================
# Main Loop
# =========================================================

while True:

    # -----------------------------------------------------
    # Camera
    # -----------------------------------------------------

    ret, frame = (
        cap.read()
    )


    if not ret:

        print(
            "카메라 프레임 읽기 실패"
        )

        break


    # -----------------------------------------------------
    # Inference
    # -----------------------------------------------------

    predictions = (
        run_inference(
            frame
        )
    )


    # -----------------------------------------------------
    # Bounding Box
    # -----------------------------------------------------

    draw_predictions(
        frame,
        predictions
    )


    # -----------------------------------------------------
    # FPS 계산
    # -----------------------------------------------------

    current_time = (
        time.perf_counter()
    )

    elapsed = (
        current_time
        - prev_time
    )

    prev_time = current_time


    if elapsed > 0:

        instant_fps = (
            1.0 / elapsed
        )

        # FPS가 너무 튀지 않도록
        # 이동 평균 형태로 계산

        if fps == 0:

            fps = instant_fps

        else:

            fps = (
                fps * 0.9
                + instant_fps * 0.1
            )


    frame_count += 1


    # -----------------------------------------------------
    # Detection 개수
    # -----------------------------------------------------

    detection_count = (
        len(predictions)
    )


    # -----------------------------------------------------
    # 화면에 FPS 표시
    # -----------------------------------------------------

    fps_text = (
        f"FPS: {fps:.1f}"
    )

    detection_text = (
        f"Plastic bottles: "
        f"{detection_count}"
    )


    cv2.putText(
        frame,

        fps_text,

        (10, 30),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0, 255, 0),

        2,
    )


    cv2.putText(
        frame,

        detection_text,

        (10, 60),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (0, 255, 0),

        2,
    )


    # -----------------------------------------------------
    # 결과 출력
    # -----------------------------------------------------

    if predictions:

        for p in predictions:

            print(
                f'Plastic Bottle | '
                f'{p["confidence"]:.2f}'
            )


    # -----------------------------------------------------
    # 화면
    # -----------------------------------------------------

    cv2.imshow(
        "Plastic Bottle Detection",
        frame
    )


    # -----------------------------------------------------
    # 종료
    # -----------------------------------------------------

    key = (
        cv2.waitKey(1)
        & 0xFF
    )


    if key == ord("q"):

        break


# =========================================================
# 종료
# =========================================================

cap.release()

cv2.destroyAllWindows()

print()
print("프로그램 종료")

