import cv2
import rclpy

from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


class CameraPub(Node):

    def __init__(self):
        super().__init__("camera_pub")

        self.width = 640
        self.height = 480

        # CvBridge 객체
        self.bridge = CvBridge()

        # 원본 영상 발행자
        self.image_pub = self.create_publisher(
            Image,
            "camera/image_raw",
            10
        )

        # Canny 에지 영상 발행자
        self.edge_pub = self.create_publisher(
            Image,
            "camera/image_edges",
            10
        )

        # 카메라 정보 발행자
        self.camera_info_pub = self.create_publisher(
            CameraInfo,
            "camera/camera_info",
            10
        )

        # GStreamer 카메라 파이프라인
        pipeline = (
            "v4l2src device=/dev/video0 ! "
            f"image/jpeg,width={self.width},height={self.height},"
            "framerate=30/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=true sync=false"
        )

        self.cap = cv2.VideoCapture(
            pipeline,
            cv2.CAP_GSTREAMER
        )

        if not self.cap.isOpened():
            raise RuntimeError(
                "카메라를 열 수 없습니다. "
                "카메라 장치와 GStreamer 설정을 확인하세요."
            )

        self.camera_info = self.create_camera_info()

        # OpenCV 출력 창 생성
        cv2.namedWindow("Camera")
        cv2.namedWindow("Canny Edge")

        # 30 FPS 타이머
        self.timer = self.create_timer(
            1.0 / 30.0,
            self.img_gen_callback
        )

        self.get_logger().info("카메라 노드가 시작되었습니다.")


    def create_camera_info(self):
        """CameraInfo 메시지를 생성합니다."""

        msg = CameraInfo()

        msg.width = self.width
        msg.height = self.height
        msg.distortion_model = "plumb_bob"

        # 왜곡 계수
        msg.d = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]

        # 예제용 카메라 내부 파라미터
        fx = 600.0
        fy = 600.0
        cx = self.width / 2.0
        cy = self.height / 2.0

        # 카메라 내부 행렬 K
        msg.k = [
            fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0
        ]

        # 보정 행렬 R
        msg.r = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0
        ]

        # 투영 행렬 P
        msg.p = [
            fx, 0.0, cx, 0.0,
            0.0, fy, cy, 0.0,
            0.0, 0.0, 1.0, 0.0
        ]

        return msg


    def img_gen_callback(self):
        """카메라 영상을 읽고 Canny를 적용합니다."""

        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warning(
                "카메라 프레임을 읽지 못했습니다."
            )
            return

        # 혹시 카메라 출력 크기가 다른 경우 크기 맞추기
        if (
            frame.shape[1] != self.width
            or frame.shape[0] != self.height
        ):
            frame = cv2.resize(
                frame,
                (self.width, self.height)
            )

        # --------------------------------------------
        # 1. Canny 에지 검출
        # --------------------------------------------

        # BGR 컬러 영상을 그레이스케일로 변환
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # 잡음 제거
        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        # Canny 에지 검출
        edges = cv2.Canny(
            blurred,
            threshold1=50,
            threshold2=150,
            apertureSize=3,
            L2gradient=True
        )

        # --------------------------------------------
        # 2. 원본 영상에 사각형 그리기
        # --------------------------------------------

        display_frame = frame.copy()

        cv2.rectangle(
            display_frame,
            (10, 10),
            (self.width - 10, self.height - 10),
            (255, 0, 0),
            3
        )

        # --------------------------------------------
        # 3. OpenCV 창 출력
        # --------------------------------------------

        cv2.imshow("Camera", display_frame)
        cv2.imshow("Canny Edge", edges)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            raise KeyboardInterrupt

        # --------------------------------------------
        # 4. OpenCV 영상을 ROS Image 메시지로 변환
        # --------------------------------------------

        # 원본 컬러 영상은 bgr8
        raw_msg = self.bridge.cv2_to_imgmsg(
            frame,
            encoding="bgr8"
        )

        # Canny 결과는 단일 채널 영상이므로 mono8
        edge_msg = self.bridge.cv2_to_imgmsg(
            edges,
            encoding="mono8"
        )

        now = self.get_clock().now().to_msg()

        raw_msg.header.stamp = now
        raw_msg.header.frame_id = "camera_link"

        edge_msg.header.stamp = now
        edge_msg.header.frame_id = "camera_link"

        self.camera_info.header.stamp = now
        self.camera_info.header.frame_id = "camera_link"

        # --------------------------------------------
        # 5. ROS 토픽 발행
        # --------------------------------------------

        self.image_pub.publish(raw_msg)
        self.edge_pub.publish(edge_msg)
        self.camera_info_pub.publish(self.camera_info)


    def cleanup(self):
        """카메라 및 OpenCV 자원을 정리합니다."""

        if self.cap.isOpened():
            self.cap.release()

        cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)

    node = None

    try:
        node = CameraPub()
        rclpy.spin(node)

    except KeyboardInterrupt:
        print("키보드 인터럽트: 카메라 노드를 종료합니다.")

    except Exception as error:
        print(f"오류가 발생했습니다: {error}")

    finally:
        if node is not None:
            node.cleanup()
            node.destroy_node()

        rclpy.try_shutdown()


if __name__ == "__main__":
    main()