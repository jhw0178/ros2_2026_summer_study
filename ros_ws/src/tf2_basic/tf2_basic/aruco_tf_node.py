

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import numpy as np


class ArucoTFNode(Node):

    def __init__(self):
        super().__init__("aruco_tf_node")

        self.bridge = CvBridge()
        self.tf_broadcaster = TransformBroadcaster(self)

        self.image_sub = self.create_subscription(Image, "/gripper_camera/image_raw", self.image_callback, 10)
        # ArUco 설정
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()
        
        self.last_ids = None
        self.last_tvecs = None
        self.last_corners = None
        self.last_rvecs = None
        
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera", 640, 480)

        self.get_logger().info("aruco_tf_node started")

        self.marker_length = 0.04   # meter (4cm)
        self.camera_matrix = np.array([[600.0, 0.0, 320.0], [0.0, 600.0, 240.0], [0.0, 0.0, 1.0]], dtype=np.float64)
        self.dist_coeffs = np.zeros((5,1),dtype=np.float64)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"CV Bridge Error : {e}")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.parameters)
        
        # ArUco 검출
        corners, ids, rejected = cv2.aruco.detectMarkers( gray, self.dictionary, parameters=self.parameters)
        # 새로 검출되면 저장
        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.marker_length, self.camera_matrix, self.dist_coeffs)
            self.last_ids = ids
            self.last_corners = corners
            self.last_tvecs = tvecs
            self.last_rvecs = rvecs

        # 마지막 검출 결과가 있으면 계속 그림
        if self.last_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, self.last_corners, self.last_ids)
            for i, marker_id in enumerate(self.last_ids):
                t = self.last_tvecs[i][0]
                r = self.last_rvecs[i][0]
                self.publish_tf(t[0], t[1], t[2], r, marker_id[0])
                px, py = self.last_corners[i][0][0]
                cv2.putText(frame, f"ID:{marker_id[0]}", (int(px), int(py)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                cv2.putText(frame, f"X:{t[0]:.3f} Y:{t[1]:.3f} Z:{t[2]:.3f}", (int(px), int(py)-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)
    
    # tf 발행 함수
    def publish_tf(self, x, y, z, rvec, marker_id):
        tf = TransformStamped()
        tf.header.stamp = self.get_clock().now().to_msg()
        tf.header.frame_id = "camera_link"
        tf.child_frame_id = f"aruco_box_top_{marker_id}"
        
        box_height = 0.05
        tf.transform.translation.x = float(x)
        tf.transform.translation.y = float(y)
        tf.transform.translation.z = float(z + box_height/2)
        
        rotation_matrix, _ = cv2.Rodrigues(rvec)
        quat = self.rotation_matrix_to_quaternion(rotation_matrix)
        tf.transform.rotation.x = quat[0]
        tf.transform.rotation.y = quat[1]
        tf.transform.rotation.z = quat[2]
        tf.transform.rotation.w = quat[3]
        self.tf_broadcaster.sendTransform(tf)
    
    # 퀀터니언 변환 함수 추가
    def rotation_matrix_to_quaternion(self, R):
        q = np.empty((4,))
        trace = np.trace(R)
        if trace > 0:
            s = 0.5 / np.sqrt(trace+1.0)
            q[3] = 0.25 / s
            q[0] = (R[2,1]-R[1,2]) * s
            q[1] = (R[0,2]-R[2,0]) * s
            q[2] = (R[1,0]-R[0,1]) * s
        else:
            i = np.argmax([R[0,0], R[1,1], R[2,2]])
            if i == 0:
                s = 2*np.sqrt(1+R[0,0]-R[1,1]-R[2,2])
                q[3]=(R[2,1]-R[1,2])/s
                q[0]=0.25*s
                q[1]=(R[0,1]+R[1,0])/s
                q[2]=(R[0,2]+R[2,0])/s
            elif i == 1:
                s=2*np.sqrt(1+R[1,1]-R[0,0]-R[2,2])
                q[3]=(R[0,2]-R[2,0])/s
                q[0]=(R[0,1]+R[1,0])/s
                q[1]=0.25*s
                q[2]=(R[1,2]+R[2,1])/s
            else:
                s=2*np.sqrt(1+R[2,2]-R[0,0]-R[1,1])
                q[3]=(R[1,0]-R[0,1])/s
                q[0]=(R[0,2]+R[2,0])/s
                q[1]=(R[1,2]+R[2,1])/s
                q[2]=0.25*s
        return q

def main(args=None):

    rclpy.init(args=args)
    node = ArucoTFNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
