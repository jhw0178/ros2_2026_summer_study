import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImgSubscriber(Node):
    def __init__(self):
        super().__init__('img_subscriber')
        cv2.namedWindow("camera")
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, "image_raw", self.img_callback, 10)

    def img_callback(self, img: Image):
        img_sub = self.bridge.imgmsg_to_cv2(img)
        cv2.imshow("camera", img_sub)
        key = cv2.waitKey(3)
        if key == ord("q"):
            raise KeyboardInterrupt
        
def main(args=None):
    rclpy.init(args=args)
    node = ImgSubscriber() 

    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        print("키보드 인터럽트") 
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()