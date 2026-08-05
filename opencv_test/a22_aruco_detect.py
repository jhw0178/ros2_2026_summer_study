####### 카메라 상에 띄워진 aruco의 종류(번호)를 맞추는(detection) 연습


### aruco가 있는지 확인
# python3 -c "import cv2; print(cv2.__version__); print(cv2.getBuildInformation())"
# aruco 설치
# sudo apt install -y python3-venv python3-full

### 가상 환경 활성화
# source .venv/bin/activate
# prp 업그레이드
# python -m pip install --upgrade pip
# python -m pip install "numpy==1.26.4"

from pathlib import Path
import cv2


def main():
    file_path = Path(__file__).parent
    pipeline = (
        "v4l2src device=/dev/video0 ! "
        "image/jpeg,width=640,height=480,framerate=30/1 ! "
        "jpegdec ! "
        "videoconvert ! "
        "video/x-raw,format=BGR ! "
        "appsink drop=true sync=false"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    # MJPG 설정

    # dictionary
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()

    previous_ids = set()

    if not cap.isOpened():
        return
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        if not ret:
            break
        # detection(탐지, 검출) 하는 코드

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()