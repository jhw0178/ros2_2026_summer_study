
import os
import cv2
import time

from concurrent.futures import ThreadPoolExecutor

from inference import get_model
import supervision as sv


# =========================================================
# Model
# =========================================================

CAN_MODEL_ID = "can-or-can-not-pwbv4/2"

PAPER_MODEL_ID = (
    "siddhants-workspace-3y7tn/"
    "crumpled-paper-detection-neac2-2-rfdetr-seg-small-t1"
)

# 새로운 플라스틱 병 모델
PLASTIC_MODEL_ID = (
    "plastic-bottles-ip5yb-uziag-hg1ll/1"
)


# =========================================================
# Threshold
# =========================================================

CAN_THRESHOLD = 0.30

PAPER_THRESHOLD = 0.93

PLASTIC_THRESHOLD = 0.50


# =========================================================
# API Key
# =========================================================

api_key = os.environ.get(
    "ROBOFLOW_API_KEY"
)

if not api_key:

    raise RuntimeError(
        "ROBOFLOW_API_KEY가 없습니다.\n"
        "터미널에서 다음 명령을 실행하세요:\n"
        "export ROBOFLOW_API_KEY='YOUR_API_KEY'"
    )


# =========================================================
# Model Loading
# =========================================================

print("====================================")
print("로컬 모델 로딩 시작")
print("====================================")


print()
print("[1/3] 캔 모델 로딩 중...")

can_model = get_model(
    model_id=CAN_MODEL_ID,
    api_key=api_key,
)

print("캔 모델 로딩 완료")


print()
print("[2/3] 구겨진 종이 모델 로딩 중...")

paper_model = get_model(
    model_id=PAPER_MODEL_ID,
    api_key=api_key,
)

print("구겨진 종이 모델 로딩 완료")


print()
print("[3/3] 플라스틱 병 모델 로딩 중...")

plastic_model = get_model(
    model_id=PLASTIC_MODEL_ID,
    api_key=api_key,
)

print("플라스틱 병 모델 로딩 완료")


print()
print("모든 모델 로딩 완료")
print("====================================")


# =========================================================
# Camera
# =========================================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_V4L2
)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)

cap.set(
    cv2.CAP_PROP_FPS,
    30
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
# Convert Result
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

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        if (
            detections.confidence
            is not None
        ):

            confidence = float(
                detections.confidence[i]
            )

        else:

            confidence = 0.0


        # -------------------------------------------------
        # Threshold
        # -------------------------------------------------

        if confidence < threshold:

            continue


        # -------------------------------------------------
        # Bounding Box
        # -------------------------------------------------

        x1, y1, x2, y2 = (
            detections.xyxy[i]
        )


        # -------------------------------------------------
        # Class
        # -------------------------------------------------

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
# Local Inference
# =========================================================

def run_inference(frame):

    results = {
        "can": [],
        "paper": [],
        "plastic": []
    }


    # =====================================================
    # CAN
    # =====================================================

    try:

        can_result = (
            can_model.infer(
                frame
            )[0]
        )

        results["can"] = (
            convert_result(
                can_result,
                CAN_THRESHOLD
            )
        )

    except Exception as e:

        print(
            "CAN inference 오류:",
            e
        )


    # =====================================================
    # PAPER
    # =====================================================

    try:

        paper_result = (
            paper_model.infer(
                frame
            )[0]
        )

        results["paper"] = (
            convert_result(
                paper_result,
                PAPER_THRESHOLD
            )
        )

    except Exception as e:

        print(
            "PAPER inference 오류:",
            e
        )


    # =====================================================
    # PLASTIC
    # =====================================================

    try:

        plastic_result = (
            plastic_model.infer(
                frame
            )[0]
        )

        results["plastic"] = (
            convert_result(
                plastic_result,
                PLASTIC_THRESHOLD
            )
        )

    except Exception as e:

        print(
            "PLASTIC inference 오류:",
            e
        )


    return results


# =========================================================
# Bounding Box
# =========================================================

def draw_predictions(
    frame,
    predictions,
    color,
    prefix
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


        # -------------------------------------------------
        # Bounding Box
        # -------------------------------------------------

        cv2.rectangle(
            frame,

            (x1, y1),
            (x2, y2),

            color,

            2,
        )


        # -------------------------------------------------
        # Label
        # -------------------------------------------------

        label = (
            f"{prefix}"
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

            color,

            2,
        )


# =========================================================
# Async Inference
# =========================================================

executor = ThreadPoolExecutor(
    max_workers=1
)

inference_future = None


last_can_predictions = []

last_paper_predictions = []

last_plastic_predictions = []


# =========================================================
# FPS
# =========================================================

fps = 0.0

fps_previous_time = (
    time.perf_counter()
)

fps_frame_count = 0

fps_update_time = (
    time.perf_counter()
)


# =========================================================
# Start
# =========================================================

print()
print("====================================")

print(
    "Local Waste Detection Start"
)

print()

print("CAN:")
print(
    CAN_MODEL_ID
)

print()

print("PAPER:")
print(
    PAPER_MODEL_ID
)

print()

print("PLASTIC:")
print(
    PLASTIC_MODEL_ID
)

print()

print(
    "Camera : 640 x 480 / 30 FPS"
)

print(
    "q : 종료"
)

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
    # FPS 계산
    # -----------------------------------------------------

    fps_frame_count += 1

    current_time = (
        time.perf_counter()
    )

    elapsed = (
        current_time
        - fps_update_time
    )


    # 0.5초마다 FPS 갱신
    if elapsed >= 0.5:

        fps = (
            fps_frame_count
            / elapsed
        )

        fps_frame_count = 0

        fps_update_time = (
            current_time
        )


    # -----------------------------------------------------
    # Inference 결과 확인
    # -----------------------------------------------------

    if (
        inference_future is not None
        and inference_future.done()
    ):

        try:

            results = (
                inference_future.result()
            )


            last_can_predictions = (
                results["can"]
            )

            last_paper_predictions = (
                results["paper"]
            )

            last_plastic_predictions = (
                results["plastic"]
            )


            # =============================================
            # CAN 출력
            # =============================================

            if last_can_predictions:

                print()

                print(
                    "--------- CAN ---------"
                )

                for p in (
                    last_can_predictions
                ):

                    print(
                        f'{p["class"]:30s} '
                        f'{p["confidence"]:.2f}'
                    )


            # =============================================
            # PAPER 출력
            # =============================================

            if last_paper_predictions:

                print()

                print(
                    "---- CRUMPLED PAPER ----"
                )

                for p in (
                    last_paper_predictions
                ):

                    print(
                        f'{p["class"]:30s} '
                        f'{p["confidence"]:.2f}'
                    )


            # =============================================
            # PLASTIC
            # =============================================

            if last_plastic_predictions:

                print()

                print(
                    "------- PLASTIC -------"
                )

                for p in (
                    last_plastic_predictions
                ):

                    print(
                        f'{p["class"]:30s} '
                        f'{p["confidence"]:.2f}'
                    )


        except Exception as e:

            print(
                "Inference 오류:",
                e
            )


        inference_future = None


    # -----------------------------------------------------
    # 새로운 inference 시작
    # -----------------------------------------------------

    if inference_future is None:

        inference_frame = (
            frame.copy()
        )


        inference_future = (
            executor.submit(
                run_inference,
                inference_frame
            )
        )


    # =====================================================
    # Bounding Box
    # =====================================================

    draw_predictions(
        frame,

        last_can_predictions,

        (0, 255, 0),

        "[CAN] "
    )


    draw_predictions(
        frame,

        last_paper_predictions,

        (0, 0, 255),

        "[PAPER] "
    )


    draw_predictions(
        frame,

        last_plastic_predictions,

        (255, 0, 0),

        "[PLASTIC] "
    )


    # =====================================================
    # Detection Count
    # =====================================================

    total_detections = (
        len(last_can_predictions)
        + len(last_paper_predictions)
        + len(last_plastic_predictions)
    )


    # =====================================================
    # FPS 표시
    # =====================================================

    cv2.putText(
        frame,

        f"FPS: {fps:.1f}",

        (10, 30),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0, 255, 0),

        2,
    )


    # =====================================================
    # Detection Count 표시
    # =====================================================

    cv2.putText(
        frame,

        f"Objects: {total_detections}",

        (10, 60),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (0, 255, 0),

        2,
    )


    # =====================================================
    # 화면
    # =====================================================

    cv2.imshow(
        "Local Waste Detection",
        frame
    )


    # -----------------------------------------------------
    # Keyboard
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


executor.shutdown(
    wait=False,
    cancel_futures=True
)


cv2.destroyAllWindows()


print()
print(
    "프로그램 종료"
)
