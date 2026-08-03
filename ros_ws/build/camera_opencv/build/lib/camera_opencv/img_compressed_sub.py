import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage


class ImgComSub(Node):
    def __init__(self):
        super().__init__('img_compressed_subscriber')
        cv2.namedWindow("camera")
        self.bridge = CvBridge()
        self.create_subscription(CompressedImage, "image_raw/compressed", self.img_callback, 10)

    def img_callback(self, msg: CompressedImage):
        img = self.bridge.compressed_imgmsg_to_cv2(msg)
        cv2.imshow("camera", img)
        key = cv2.waitKey(3)
        if key == ord("q"):
            raise KeyboardInterrupt
        
def main(args=None):
    rclpy.init(args=args)
    node = ImgComSub() 

    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        print("키보드 인터럽트") 
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()