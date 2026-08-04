import rclpy
from rclpy.node import Node

import cv2
import numpy as np

from . import color

class DrawingCamera(Node):

    WIDTH = 640
    HEIGHT = 480
    FPS = 30

    def __init__(self):
        super().__init__("drawing_camera")

        # GStreamer 카메라 연결
        pipeline = (
            "v4l2src device=/dev/video0 ! "
            "image/jpeg,width=640,height=480,"
            "framerate=30/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=true sync=false"
        )

        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error("카메라 연결 실패")
            raise RuntimeError("camera open failed")

        self.get_logger().info("카메라 연결 성공")

        # 그림 관련 변수
        self.option = [0]
        self.old_x = None
        self.old_y = None
        self.canvas = np.zeros((self.HEIGHT,self.WIDTH,3), dtype=np.uint8)

        # OpenCV Window
        cv2.namedWindow("camera")
        cv2.setMouseCallback("camera", self.onMouse)

        # ROS timer
        self.timer = self.create_timer(1.0/self.FPS, self.camera_callback)

    # Mouse Event
    def onMouse(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.old_x = x
            self.old_y = y
            cv2.circle(self.canvas, (x,y), 3, color.RED, -1)
            print("마우스 버튼 클릭")

        elif (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
            if self.old_x is not None:
                cv2.line(self.canvas, (self.old_x,self.old_y), (x,y), list(color.COLORS.values())[self.option[0]], 2)
            self.old_x=x
            self.old_y=y
            print("드래그")
        elif event == cv2.EVENT_MOUSEMOVE:
            print("마우스 움직임")

    # Camera Callback

    def camera_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warning("frame read failed")
            return
        frame=cv2.resize(frame, (self.WIDTH,self.HEIGHT))
        
        # 카메라 + 그림 합성
        result=cv2.add(frame, self.canvas)
        cv2.imshow("camera", result)
        key=cv2.waitKey(1)&0xff

        if key == ord("q"):
            rclpy.shutdown()
        elif key == ord(" "):
            self.option[0]+=1
            if self.option[0]>=len(color.COLORS):
                self.option[0]=0

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node=DrawingCamera()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__=="__main__":
    main()