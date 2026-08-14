import cv2
import numpy as np


# =========================================================
# Camera 설정
# =========================================================

CAMERA_DEVICE = "/dev/video0"

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30


# =========================================================
# ArUco 설정
# =========================================================

ARUCO_DICT = cv2.aruco.DICT_4X4_50

TARGET_IDS = [1, 2, 3, 4]

aruco_dictionary = cv2.aruco.getPredefinedDictionary(
    ARUCO_DICT
)

aruco_parameters = cv2.aruco.DetectorParameters()

aruco_detector = cv2.aruco.ArucoDetector(
    aruco_dictionary,
    aruco_parameters
)


# =========================================================
# Camera
# =========================================================

cap = cv2.VideoCapture(
    CAMERA_DEVICE,
    cv2.CAP_V4L2
)

if not cap.isOpened():
    raise RuntimeError(
        "C920 카메라를 열 수 없습니다."
    )


# =========================================================
# C920 설정
# =========================================================

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG")
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
    cv2.CAP_PROP_BUFFERSIZE,
    1
)


# =========================================================
# 실제 카메라 설정 확인
# =========================================================

print()
print("==========================================")
print("       C920 + ArUco Detection")
print("==========================================")

print("Device :", CAMERA_DEVICE)

print(
    "Width  :",
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

print(
    "Height :",
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

print(
    "FPS    :",
    cap.get(cv2.CAP_PROP_FPS)
)

print("Target IDs :", TARGET_IDS)

print()
print("q : 종료")
print("==========================================")
print()


# =========================================================
# ArUco 검출 함수
# =========================================================

def detect_aruco(frame):

    # -----------------------------------------------------
    # Grayscale
    # -----------------------------------------------------

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------------------------------
    # ArUco Detection
    # -----------------------------------------------------

    corners, ids, rejected = aruco_detector.detectMarkers(
        gray
    )

    detected_markers = {}

    # -----------------------------------------------------
    # 검출된 마커가 없는 경우
    # -----------------------------------------------------

    if ids is None:
        return detected_markers

    ids = ids.flatten()

    # -----------------------------------------------------
    # 각각의 마커 처리
    # -----------------------------------------------------

    for i, marker_id in enumerate(ids):

        marker_id = int(marker_id)

        # 1~4번만 사용
        if marker_id not in TARGET_IDS:
            continue

        # -------------------------------------------------
        # 해당 ArUco의 네 꼭짓점
        # -------------------------------------------------

        marker_corners = corners[i][0]

        # -------------------------------------------------
        # 중심 좌표 계산
        # -------------------------------------------------

        center_x = int(
            np.mean(marker_corners[:, 0])
        )

        center_y = int(
            np.mean(marker_corners[:, 1])
        )

        # -------------------------------------------------
        # 결과 저장
        # -------------------------------------------------

        detected_markers[marker_id] = {
            "center": (
                center_x,
                center_y
            ),

            "corners": marker_corners
        }

    return detected_markers


# =========================================================
# ArUco 화면 표시
# =========================================================

def draw_aruco(
    frame,
    detected_markers
):

    for marker_id, data in detected_markers.items():

        corners = data["corners"]

        center_x, center_y = data["center"]

        # -------------------------------------------------
        # ArUco 외곽선
        # -------------------------------------------------

        points = corners.astype(
            np.int32
        )

        cv2.polylines(
            frame,
            [points],
            True,
            (0, 255, 0),
            2
        )

        # -------------------------------------------------
        # 중심 파란 점
        #
        # BGR
        # 파란색 = (255, 0, 0)
        # -------------------------------------------------

        cv2.circle(
            frame,
            (center_x, center_y),
            6,
            (255, 0, 0),
            -1
        )

        # -------------------------------------------------
        # ID 표시
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"ID: {marker_id}",
            (
                center_x + 10,
                center_y - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        # -------------------------------------------------
        # 픽셀 좌표 표시
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"({center_x}, {center_y})",
            (
                center_x + 10,
                center_y + 5
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2
        )


# =========================================================
# Main Loop
# =========================================================

while True:

    # -----------------------------------------------------
    # Camera Frame
    # -----------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print(
            "카메라 프레임 읽기 실패"
        )

        break


    # -----------------------------------------------------
    # ArUco Detection
    # -----------------------------------------------------

    detected_markers = detect_aruco(
        frame
    )


    # -----------------------------------------------------
    # 화면에 ArUco 표시
    # -----------------------------------------------------

    draw_aruco(
        frame,
        detected_markers
    )


    # =====================================================
    # 검출된 ID 표시
    # =====================================================

    detected_ids = sorted(
        detected_markers.keys()
    )

    cv2.putText(
        frame,
        f"Detected IDs: {detected_ids}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )


    # =====================================================
    # 4개 모두 검출 여부
    # =====================================================

    all_detected = all(
        marker_id in detected_markers
        for marker_id in TARGET_IDS
    )

    if all_detected:

        cv2.putText(
            frame,
            "ALL 4 MARKERS DETECTED",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            frame,
            "WAITING FOR MARKERS...",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


    # =====================================================
    # 터미널에 좌표 출력
    # =====================================================

    if detected_markers:

        output = []

        for marker_id in sorted(
            detected_markers.keys()
        ):

            x, y = detected_markers[
                marker_id
            ]["center"]

            output.append(
                f"ID {marker_id}: "
                f"({x}, {y})"
            )

        print(
            " | ".join(output)
        )


    # =====================================================
    # 화면 출력
    # =====================================================

    cv2.imshow(
        "C920 + ArUco",
        frame
    )


    # =====================================================
    # 종료
    # =====================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


# =========================================================
# 종료
# =========================================================

cap.release()

cv2.destroyAllWindows()

print()
print("프로그램 종료")