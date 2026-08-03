import rclpy
from rclpy.node import Node
import cv2
import numpy as np

class ImgShow(Node):
    def __init__(self):
        super().__init__("img_show_node") 
        self.create_timer(1 / 30, self.img_gen_callback)
        cv2.namedWindow("camera")
        self.img = np.zeros([300, 300], dtype=np.uint8)
        self.brightness = 0

    def img_gen_callback(self):
        self.brightness += 1
        self.img.fill(self.brightness)
        cv2.imshow("camera", self.img)
        if self.brightness > 255:
            self.brightness = 0
        key = cv2.waitKey(30)
        if key == ord("q"):
            raise KeyboardInterrupt

def main(args=None):
    rclpy.init(args=args)
    node = ImgShow() 

    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        print("키보드 인터럽트") 
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()