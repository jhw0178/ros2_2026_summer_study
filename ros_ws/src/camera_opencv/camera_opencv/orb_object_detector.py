from pathlib import Path

import cv2
import numpy as np
import rclpy

from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


class OrbObjectDetector(Node):
    """
    기준 사진과 실시간 카메라 프레임을 ORB로 비교하여
    물체를 검출하는 ROS 2 노드입니다.

    기존 a34_orb.py의 다음 방식을 유지합니다.

    1. ORB 특징점과 기술자 계산
    2. BFMatcher + Hamming 거리 + crossCheck
    3. 거리 기준으로 좋은 매칭 선택
    4. cv2.drawMatches()로 매칭선 표시
    5. RANSAC으로 호모그래피 계산
    6. 기준 사진 외곽선을 카메라 영상에 투영
    """
    
    def __init__(self):
        super().__init__("orb_object_detector")
        # 1. ROS 2 파라미터 선언
        # 이 기본 경로를 사용자가 촬영한 기준 사진으로 변경하세요.
        self.declare_parameter("reference_image", str( Path.home() / "ros2_2026_summer_study" / "opencv_test" / "data" / "wor.jpg"),)
        self.declare_parameter("camera_device", "/dev/video0")
        self.declare_parameter("width", 640)
        self.declare_parameter("height", 480)
        self.declare_parameter("fps", 30)
        # ORB 설정
        self.declare_parameter("nfeatures", 1000)
        # a34_orb.py의 5 * min_distance에 해당
        self.declare_parameter("distance_multiplier", 5.0)
        # 최소 거리가 0 또는 지나치게 작은 경우를 위한 하한값
        self.declare_parameter("minimum_distance_threshold", 30.0)
        # 호모그래피 계산 전 필요한 최소 good match 개수
        self.declare_parameter("min_good_matches", 5)
        # 검출 성공으로 판단할 최소 RANSAC 인라이어 개수
        self.declare_parameter("min_inliers", 4)
        # RANSAC 재투영 오차 임계값
        self.declare_parameter("ransac_threshold", 3.0)
        # 2. 파라미터 값 가져오기
        self.reference_image_path = str(self.get_parameter("reference_image").value)
        self.camera_device = str(self.get_parameter("camera_device").value)
        self.width = int(self.get_parameter("width").value)
        self.height = int(self.get_parameter("height").value)
        self.fps = int(self.get_parameter("fps").value)
        self.nfeatures = int(self.get_parameter("nfeatures").value)
        self.distance_multiplier = float(self.get_parameter("distance_multiplier").value)
        self.minimum_distance_threshold = float(self.get_parameter("minimum_distance_threshold").value)
        self.min_good_matches = int(self.get_parameter("min_good_matches").value)
        self.min_inliers = int(self.get_parameter("min_inliers").value)
        self.ransac_threshold = float(self.get_parameter("ransac_threshold").value)
        # 3. ROS Publisher와 CvBridge 생성
        self.bridge = CvBridge()
        # 원본 카메라 영상
        self.raw_image_pub = self.create_publisher(Image, "camera/image_raw", 10)
        # 기준 사진과 카메라 프레임의 매칭 결과
        self.match_image_pub = self.create_publisher(Image, "camera/orb_matches", 10)
        # 물체 외곽선이 표시된 카메라 영상
        self.detection_image_pub = self.create_publisher(Image, "camera/orb_detection", 10)
        self.camera_info_pub = self.create_publisher(CameraInfo, "camera/camera_info", 10)
        self.camera_info = self.create_camera_info()
        # 4. 기준 이미지 불러오기
        self.reference_color = cv2.imread(self.reference_image_path, cv2.IMREAD_COLOR)
        if self.reference_color is None:
            raise FileNotFoundError("기준 이미지를 불러올 수 없습니다: " f"{self.reference_image_path}")
        self.reference_gray = cv2.cvtColor(self.reference_color, cv2.COLOR_BGR2GRAY,)
        # 5. ORB 생성 및 기준 이미지 특징 계산
        self.orb = cv2.ORB_create(nfeatures=self.nfeatures)
        (self.reference_keypoints, self.reference_descriptors) = self.orb.detectAndCompute(self.reference_gray, None)
        if (self.reference_descriptors is None or len(self.reference_keypoints) == 0):
            raise RuntimeError("기준 이미지에서 ORB 특징점 또는 " "기술자를 계산하지 못했습니다.")
        self.get_logger().info("기준 이미지 ORB 특징점 수: " f"{len(self.reference_keypoints)}")
        # 6. a34_orb.py와 동일한 BFMatcher 생성
        # ORB 기술자는 이진 기술자이므로 NORM_HAMMING 사용
        # crossCheck=True로 양방향에서 일치하는 매칭만 선택
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # 7. 카메라 열기
        pipeline = (f"v4l2src device={self.camera_device} ! "
            f"image/jpeg,width={self.width},"
            f"height={self.height},"
            f"framerate={self.fps}/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=true max-buffers=1 sync=false"
        )
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            self.get_logger().warning("GStreamer로 카메라를 열지 못했습니다. " "V4L2 직접 연결을 시도합니다.")
            self.cap.release()
            camera_index = self.get_camera_index(self.camera_device)
            self.cap = cv2.VideoCapture(camera_index,cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.cap.isOpened():
            raise RuntimeError(f"카메라를 열 수 없습니다: {self.camera_device}")
        # 8. 출력 창 생성
        # a34_orb.py의 dst에 해당
        cv2.namedWindow("Good Matches", cv2.WINDOW_NORMAL)
        # a34_orb.py의 dst2에 해당
        cv2.namedWindow("ORB Homography", cv2.WINDOW_NORMAL)
        # 창이 지나치게 크게 열리는 것을 방지
        cv2.resizeWindow("Good Matches", 1200, 600)
        cv2.resizeWindow("ORB Homography", 1200, 600)
        # 9. 기타 상태 변수
        self.frame_count = 0
        self.shutdown_requested = False
        # 10. 30 FPS 타이머
        self.timer = self.create_timer(1.0 / float(self.fps), self.image_callback)
        self.get_logger().info(f"기준 이미지: {self.reference_image_path}")
        self.get_logger().info(f"카메라: {self.camera_device}")
        self.get_logger().info("ORB 물체 검출 노드가 시작되었습니다.")
        self.get_logger().info("q 키를 누르면 종료합니다.")
    @staticmethod
    
    def get_camera_index(device_path: str) -> int:
        """
        /dev/video0과 같은 경로에서 카메라 번호를 추출합니다.
        """

        device_name = Path(device_path).name
        if device_name.startswith("video"):
            index_text = device_name.replace("video", "", 1)
            if index_text.isdigit():
                return int(index_text)
        return 0
    
    def create_camera_info(self) -> CameraInfo:
        """
        CameraInfo 메시지를 생성합니다.

        현재 내부 파라미터는 예제 값입니다.
        정밀 측정에는 실제 카메라 캘리브레이션 결과를 사용해야 합니다.
        """

        msg = CameraInfo()
        msg.width = self.width
        msg.height = self.height
        msg.distortion_model = "plumb_bob"
        msg.d = [0.0, 0.0, 0.0, 0.0, 0.0]
        fx = 600.0
        fy = 600.0
        cx = self.width / 2.0
        cy = self.height / 2.0
        # 카메라 내부 행렬 K
        msg.k = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
        # Rectification 행렬 R
        msg.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        # Projection 행렬 P
        msg.p = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        return msg

    def select_good_matches(self, frame_descriptors: np.ndarray):
        """
        a34_orb.py 방식으로 기술자를 매칭하고
        거리 기준으로 good match를 선택합니다.
        """

        matches = self.matcher.match(self.reference_descriptors, frame_descriptors)
        if len(matches) == 0:
            return [], [], 0.0, 0.0
        # Hamming 거리가 작은 순서대로 정렬
        matches = sorted(matches, key=lambda match: match.distance)
        min_distance = float(matches[0].distance)
        # 기존 a34_orb.py의 5 * minDist를 유지합니다.
        # 다만 min_distance가 0이면 임계값 역시 0이 되어
        # 아무 매칭도 선택되지 않을 수 있으므로
        # 최소 임계값을 추가합니다.
        distance_threshold = max(self.distance_multiplier * min_distance, self.minimum_distance_threshold)
        good_matches = [match for match in matches if match.distance <= distance_threshold]
        return (matches, good_matches, min_distance, distance_threshold)
    @staticmethod
    
    def add_status_text(image: np.ndarray, lines: list[str], color=(0, 255, 255)) -> None:
        """
        결과 영상 왼쪽 위에 상태 정보를 표시합니다.
        """

        for index, text in enumerate(lines):
            position_y = 30 + index * 27
            # 가독성을 위한 검은색 외곽선
            cv2.putText(image, text, (15, position_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(image, text, (15, position_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA)

    def create_empty_match_view(self, frame: np.ndarray, frame_keypoints, status: str) -> np.ndarray:
        """
        매칭이 없더라도 기준 사진과 카메라 프레임을
        나란히 표시합니다.
        """

        view = cv2.drawMatches(self.reference_color, self.reference_keypoints, frame, frame_keypoints, [], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        self.add_status_text(view, [status], color=(0, 0, 255))
        return view

    def process_frame(self, frame: np.ndarray):
        """
        실시간 카메라 프레임에 ORB 매칭과
        호모그래피를 적용합니다.
        """

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 1. 현재 카메라 프레임 특징점 및 기술자 계산
        (frame_keypoints, frame_descriptors) = self.orb.detectAndCompute(frame_gray, None)
        if (frame_descriptors is None or len(frame_keypoints) == 0):
            empty_view = self.create_empty_match_view(frame, frame_keypoints, "No ORB descriptors in camera frame")
            return (frame.copy(), empty_view, empty_view.copy(), 0, 0, 0)
        # 2. a34_orb.py 방식으로 기술자 매칭
        (matches, good_matches, min_distance, distance_threshold) = self.select_good_matches(frame_descriptors)
        # 3. RANSAC 적용 전 good matches 표시
        # 기존 a34_orb.py의 다음 코드에 해당합니다.
        # dst = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=2)
        good_match_view = cv2.drawMatches(self.reference_color, self.reference_keypoints, frame, frame_keypoints, good_matches, None, matchColor=(0, 255, 0), singlePointColor=None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        self.add_status_text(good_match_view,[
                f"Reference keypoints: {len(self.reference_keypoints)}",
                f"Frame keypoints: {len(frame_keypoints)}",
                f"All matches: {len(matches)}",
                f"Good matches: {len(good_matches)}",
                (
                    f"Min distance: {min_distance:.1f}, "
                    f"threshold: {distance_threshold:.1f}"
                ),
            ],
        )
        # 외곽선을 그릴 카메라 영상
        frame_with_polygon = frame.copy()
        # 좋은 매칭이 부족하면 호모그래피를 계산하지 않음
        if len(good_matches) < self.min_good_matches:
            self.add_status_text(frame_with_polygon, ["NOT DETECTED", (f"Good matches: " f"{len(good_matches)}/" f"{self.min_good_matches}")], color=(0, 0, 255))
            homography_view = cv2.drawMatches(
                self.reference_color,
                self.reference_keypoints,
                frame_with_polygon,
                frame_keypoints,
                good_matches,
                None,
                matchColor=(0, 255, 0),
                singlePointColor=None,
                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
            )
            self.add_status_text(homography_view, ["Homography not calculated", f"Good matches: {len(good_matches)}"], color=(0, 0, 255),)
            return (frame_with_polygon, good_match_view, homography_view, len(frame_keypoints), len(good_matches), 0)
        # 4. 대응점 좌표 생성
        # a34_orb.py의 src1_pts, src2_pts에 해당합니다.
        reference_points = np.float32([self.reference_keypoints[match.queryIdx].pt for match in good_matches]).reshape(-1, 1, 2)
        frame_points = np.float32([frame_keypoints[match.trainIdx].pt for match in good_matches]).reshape(-1, 1, 2)
        # 5. RANSAC 호모그래피 계산
        homography, mask = cv2.findHomography(reference_points, frame_points, cv2.RANSAC, self.ransac_threshold)
        if homography is None or mask is None:
            self.add_status_text(frame_with_polygon, ["NOT DETECTED", "Homography calculation failed"], color=(0, 0, 255))
            homography_view = cv2.drawMatches(
                self.reference_color,
                self.reference_keypoints,
                frame_with_polygon,
                frame_keypoints,
                good_matches,
                None,
                matchColor=(0, 255, 0),
                singlePointColor=None,
                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
            )
            return (frame_with_polygon, good_match_view, homography_view, len(frame_keypoints), len(good_matches), 0)
        # RANSAC 결과:
        # 1이면 올바른 매칭인 인라이어
        # 0이면 잘못된 매칭인 아웃라이어
        inlier_mask = (mask.ravel().astype(np.uint8).tolist())
        inlier_count = int(np.count_nonzero(mask))
        # 6. 기준 사진의 네 모서리를 카메라에 투영
        if inlier_count >= self.min_inliers:
            reference_height, reference_width = (
                self.reference_gray.shape
            )

            reference_corners = np.float32(
                [
                    [0, 0],
                    [0, reference_height - 1],
                    [
                        reference_width - 1,
                        reference_height - 1,
                    ],
                    [reference_width - 1, 0],
                ]
            ).reshape(-1, 1, 2)
            transformed_corners = (cv2.perspectiveTransform(reference_corners, homography))
            # 사용자가 제시한 예시와 같이 파란색 외곽선
            cv2.polylines(frame_with_polygon, [np.int32(np.round(transformed_corners))], isClosed=True, color=(255, 0, 0), thickness=3, lineType=cv2.LINE_AA)
            self.add_status_text(frame_with_polygon, ["OBJECT DETECTED", f"Good matches: {len(good_matches)}", f"RANSAC inliers: {inlier_count}"], color=(0, 255, 0))
        else:
            self.add_status_text(
                frame_with_polygon,
                [
                    "NOT DETECTED",
                    f"Good matches: {len(good_matches)}",
                    (
                        f"RANSAC inliers: "
                        f"{inlier_count}/"
                        f"{self.min_inliers}"
                    ),
                ],
                color=(0, 0, 255),
            )
        # 7. RANSAC 인라이어만 녹색 선으로 표시
        # 기존 a34_orb.py의 dst2에 해당합니다.
        draw_parameters = {
            "matchColor": (0, 255, 0),
            "singlePointColor": None,
            "matchesMask": inlier_mask,
            "flags": cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        }
        homography_view = cv2.drawMatches(
            self.reference_color,
            self.reference_keypoints,
            frame_with_polygon,
            frame_keypoints,
            good_matches,
            None,
            **draw_parameters,
        )
        detection_text = ("OBJECT DETECTED" if inlier_count >= self.min_inliers else "HOMOGRAPHY UNSTABLE")
        detection_color = ((0, 255, 0) if inlier_count >= self.min_inliers else (0, 0, 255))
        self.add_status_text(
            homography_view,
            [
                detection_text,
                f"Good matches: {len(good_matches)}",
                f"RANSAC inliers: {inlier_count}",
            ],
            color=detection_color,
        )
        return (frame_with_polygon, good_match_view, homography_view, len(frame_keypoints), len(good_matches), inlier_count)
    def image_callback(self):
        """
        카메라 프레임을 읽고 ORB 검출 결과를 출력·발행합니다.
        """

        ret, frame = self.cap.read()

        if not ret or frame is None:
            self.get_logger().warning("카메라 프레임을 읽지 못했습니다.")
            return
        # 실제 카메라 해상도가 파라미터와 다를 경우 조정
        if (frame.shape[1] != self.width or frame.shape[0] != self.height):
            frame = cv2.resize(frame, (self.width, self.height))
        (detection_frame, good_match_view, homography_view, frame_keypoint_count, good_match_count, inlier_count) = self.process_frame(frame)
        # OpenCV 창 출력
        cv2.imshow("Good Matches", good_match_view)
        cv2.imshow("ORB Homography", homography_view)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            self.get_logger().info("q 키가 입력되어 종료합니다.")
            self.shutdown_requested = True
            self.timer.cancel()
            if rclpy.ok():
                rclpy.shutdown()
            return
        # 일정 주기마다 검출 상태 로그 출력
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            self.get_logger().info(f"frame keypoints={frame_keypoint_count}, " f"good matches={good_match_count}, " f"inliers={inlier_count}")
        # ROS Image 메시지 발행
        now = self.get_clock().now().to_msg()
        raw_message = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        detection_message = self.bridge.cv2_to_imgmsg(detection_frame, encoding="bgr8")
        match_message = self.bridge.cv2_to_imgmsg(homography_view, encoding="bgr8")
        raw_message.header.stamp = now
        raw_message.header.frame_id = "camera_link"
        detection_message.header.stamp = now
        detection_message.header.frame_id = "camera_link"
        match_message.header.stamp = now
        match_message.header.frame_id = "camera_link"
        self.camera_info.header.stamp = now
        self.camera_info.header.frame_id = "camera_link"
        self.raw_image_pub.publish(raw_message)
        self.detection_image_pub.publish(detection_message)
        self.match_image_pub.publish(match_message)
        self.camera_info_pub.publish(self.camera_info)

    def cleanup(self):
        """
        카메라와 OpenCV 자원을 정리합니다.
        """

        if hasattr(self, "timer"):
            self.timer.cancel()
        if (hasattr(self, "cap") and self.cap is not None and self.cap.isOpened()):
            self.cap.release()
        cv2.destroyAllWindows()
        
def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = OrbObjectDetector()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("키보드 인터럽트: 노드를 종료합니다.")
    except ExternalShutdownException:
        pass
    except Exception as error:
        print(f"오류가 발생했습니다: {error}")
        raise
    finally:
        if node is not None:
            node.cleanup()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()