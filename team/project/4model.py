
import os
import cv2
import time

from concurrent.futures import ThreadPoolExecutor

from inference import get_model
import supervision as sv


# =========================================================
# 모델 설정
# =========================================================

# ---------------------------------------------------------
# PET 병
# ---------------------------------------------------------
PLASTIC_MODEL_ID = (
    "plastic-bottles-ip5yb-uziag-hg1ll/1"
)

# ---------------------------------------------------------
# CAN / BOTTLE 검출
# bottle / can 2-class
# ---------------------------------------------------------
CAN_MODEL_ID = (
    "cans-and-bottles-n2gns/3"
)

# ---------------------------------------------------------
# 구겨진 종이
# 기존에 사용하던 모델
# ---------------------------------------------------------
PAPER_MODEL_ID = (
    "siddhants-workspace-3y7tn/"
    "crumpled-paper-detection-neac2-2-rfdetr-seg-small-t1"
)

# ---------------------------------------------------------
# 찌그러진 캔
#
# 주의:
# 정확한 2-class 모델 ID를 확인한 후 여기에 입력하세요.
#
# 예:
# CRUSHED_CAN_MODEL_ID = "workspace/project/version"
# ---------------------------------------------------------
CRUSHED_CAN_MODEL_ID = None


# =========================================================
# Confidence Threshold
# =========================================================

PLASTIC_THRESHOLD = 0.50
CAN_THRESHOLD = 0.40
PAPER_THRESHOLD = 0.43
CRUSHED_CAN_THRESHOLD = 0.50


# =========================================================
# Camera
# =========================================================

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30


# =========================================================
# API Key
# =========================================================

api_key = os.environ.get(
    "ROBOFLOW_API_KEY"
)

if not api_key:

    raise RuntimeError(
        "\n"
        "ROBOFLOW_API_KEY가 설정되지 않았습니다.\n\n"
        "터미널에서 다음 명령을 실행하세요:\n\n"
        "export ROBOFLOW_API_KEY='YOUR_API_KEY'\n\n"
        "그리고 다시 실행하세요.\n"
    )


# =========================================================
# 시작
# =========================================================

print("====================================")
print("Waste Detection System")
print("====================================")
print()
print("API Key: 설정됨")
print()


# =========================================================
# 모델 로딩
# =========================================================

print("[1/4] Plastic Bottle 모델 로딩 중...")

plastic_model = get_model(
    model_id=PLASTIC_MODEL_ID,
    api_key=api_key,
)

print("Plastic Bottle 모델 로딩 완료")
print()


print("[2/4] Can 모델 로딩 중...")

can_model = get_model(
    model_id=CAN_MODEL_ID,
    api_key=api_key,
)

print("Can 모델 로딩 완료")
print()


print("[3/4] Crumpled Paper 모델 로딩 중...")

paper_model = get_model(
    model_id=PAPER_MODEL_ID,
    api_key=api_key,
)

print("Crumpled Paper 모델 로딩 완료")
print()


# =========================================================
# Crushed Can 모델
# =========================================================

crushed_can_model = None


if CRUSHED_CAN_MODEL_ID is not None:

    print("[4/4] Crushed Can 모델 로딩 중...")

    crushed_can_model = get_model(
        model_id=CRUSHED_CAN_MODEL_ID,
        api_key=api_key,
    )

    print("Crushed Can 모델 로딩 완료")

else:

    print("[4/4] Crushed Can 모델")

    print(
        "주의: "
        "CRUSHED_CAN_MODEL_ID가 설정되지 않았습니다."
    )

    print(
        "현재는 Crushed Can 검출을 건너뜁니다."
    )


print()
print("====================================")
print("모든 모델 로딩 완료")
print("====================================")
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
    cv2.VideoWriter_fourcc(
        *"MJPG"
    )
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
# Inference
# =========================================================

def run_inference(frame):

    results = {

        "plastic": [],

        "can": [],

        "paper": [],

        "crushed_can": [],
    }


    # =====================================================
    # 1. Plastic Bottle
    # =====================================================

    try:

        result = (
            plastic_model.infer(
                frame
            )[0]
        )

        results["plastic"] = (
            convert_result(
                result,
                PLASTIC_THRESHOLD
            )
        )

    except Exception as e:

        print(
            "Plastic inference 오류:",
            e
        )


    # =====================================================
    # 2. Can
    # =====================================================

    try:

        result = (
            can_model.infer(
                frame
            )[0]
        )

        results["can"] = (
            convert_result(
                result,
                CAN_THRESHOLD
            )
        )

    except Exception as e:

        print(
            "Can inference 오류:",
            e
        )


    # =====================================================
    # 3. Crumpled Paper
    # =====================================================

    try:

        result = (
            paper_model.infer(
                frame
            )[0]
        )

        results["paper"] = (
            convert_result(
                result,
                PAPER_THRESHOLD
            )
        )

    except Exception as e:

        print(
            "Paper inference 오류:",
            e
        )


    # =====================================================
    # 4. Crushed Can
    # =====================================================

    if crushed_can_model is not None:

        try:

            result = (
                crushed_can_model.infer(
                    frame
                )[0]
            )

            results["crushed_can"] = (
                convert_result(
                    result,
                    CRUSHED_CAN_THRESHOLD
                )
            )

        except Exception as e:

            print(
                "Crushed Can inference 오류:",
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
# 비동기 Inference
# =========================================================

executor = ThreadPoolExecutor(
    max_workers=1
)

inference_future = None


# =========================================================
# 마지막 Detection 결과
# =========================================================

last_predictions = {

    "plastic": [],

    "can": [],

    "paper": [],

    "crushed_can": [],
}


# =========================================================
# FPS
# =========================================================

fps = 0.0

prev_time = (
    time.perf_counter()
)


# =========================================================
# 시작 메시지
# =========================================================

print()
print("====================================")
print("Waste Detection Start")
print("====================================")
print()

print("PLASTIC:")
print(PLASTIC_MODEL_ID)

print()

print("CAN:")
print(CAN_MODEL_ID)

print()

print("PAPER:")
print(PAPER_MODEL_ID)

print()

if CRUSHED_CAN_MODEL_ID:

    print("CRUSHED CAN:")
    print(CRUSHED_CAN_MODEL_ID)

else:

    print(
        "CRUSHED CAN:"
        " 모델 미설정"
    )

print()

print(
    f"Camera : "
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


    # =====================================================
    # 완료된 Inference 결과 가져오기
    # =====================================================

    if (
        inference_future is not None
        and inference_future.done()
    ):

        try:

            last_predictions = (
                inference_future.result()
            )


        except Exception as e:

            print(
                "Inference 결과 오류:",
                e
            )


        inference_future = None


    # =====================================================
    # 새로운 Inference 시작
    # =====================================================

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
    # Plastic Bottle
    # =====================================================

    draw_predictions(

        frame,

        last_predictions[
            "plastic"
        ],

        (255, 0, 0),

        "[PLASTIC] "
    )


    # =====================================================
    # Can
    # =====================================================

    draw_predictions(

        frame,

        last_predictions[
            "can"
        ],

        (0, 255, 0),

        "[CAN] "
    )


    # =====================================================
    # Crumpled Paper
    # =====================================================

    draw_predictions(

        frame,

        last_predictions[
            "paper"
        ],

        (0, 0, 255),

        "[PAPER] "
    )


    # =====================================================
    # Crushed Can
    # =====================================================

    draw_predictions(

        frame,

        last_predictions[
            "crushed_can"
        ],

        (0, 165, 255),

        "[CRUSHED CAN] "
    )


    # =====================================================
    # FPS 계산
    # =====================================================

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


        if fps == 0:

            fps = instant_fps

        else:

            fps = (
                fps * 0.9
                + instant_fps * 0.1
            )


    # =====================================================
    # Detection Count
    # =====================================================

    plastic_count = len(
        last_predictions[
            "plastic"
        ]
    )

    can_count = len(
        last_predictions[
            "can"
        ]
    )

    paper_count = len(
        last_predictions[
            "paper"
        ]
    )

    crushed_can_count = len(
        last_predictions[
            "crushed_can"
        ]
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
    # Detection 개수 표시
    # =====================================================

    cv2.putText(

        frame,

        f"Plastic: {plastic_count}",

        (10, 60),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.60,

        (255, 0, 0),

        2,
    )


    cv2.putText(

        frame,

        f"Can: {can_count}",

        (10, 85),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.60,

        (0, 255, 0),

        2,
    )


    cv2.putText(

        frame,

        f"Crushed Can: "
        f"{crushed_can_count}",

        (10, 110),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.60,

        (0, 165, 255),

        2,
    )


    cv2.putText(

        frame,

        f"Paper: {paper_count}",

        (10, 135),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.60,

        (0, 0, 255),

        2,
    )


    # =====================================================
    # 화면
    # =====================================================

    cv2.imshow(

        "Waste Detection",

        frame
    )


    # =====================================================
    # Keyboard
    # =====================================================

    key = (

        cv2.waitKey(1)

        & 0xFF
    )


    if key == ord("q"):

        break


# =========================================================
# 종료
# =========================================================

print()
print("프로그램 종료 중...")


cap.release()


executor.shutdown(

    wait=False,

    cancel_futures=True
)


cv2.destroyAllWindows()


print("프로그램 종료")

