import cv2
import numpy as np
import color


def onMouse(event, x, y, flags, param):
    img = param
    # old_x, old_y = 0, 0
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img, (x, y), 1, color.RED, 5)
        print("마우스 버튼 클릭")
        onMouse.old_x = x       # 함수 속성 변수 (c의 static 처럼 활용 가능)
        onMouse.old_y = y
    if flags == cv2.EVENT_FLAG_LBUTTON and event == cv2.EVENT_MOUSEMOVE:
        print("드래그")
        cv2.line(img, (onMouse.old_x, onMouse.old_y), (x, y), color.SKYBLUE, 2)
        onMouse.old_x = x
        onMouse.old_y = y
    elif event == cv2.EVENT_MOUSEMOVE:
        print("마우스 움직임")
    cv2.imshow("canvas", img)
    

def main():
    cv2.namedWindow("canvas")
    img = np.zeros([300, 700, 3], dtype=np.uint8)
    cv2.setMouseCallback("canvas", onMouse, img)
    
    pt1, pt2 = (180, 150), (550, 150)
    size = (120, 60)
    
    cv2.circle(img, pt1, 1, color.RED, 2)
    cv2.circle(img, pt2, 1, color.RED, 2)
    
    cv2.ellipse(img, pt1, size, 0, 0, 360, color.BLUE, 1)   # type = ignore
    cv2.ellipse(img, pt2, size, 90, 0, 360, color.BLUE, 1)  # type = ignore
    cv2.ellipse(img, pt1, size, 0, 30, 270, color.ORANGE, 1)  # type = ignore
    cv2.ellipse(img, pt2, size, 90, -45, 90, color.ORANGE, 1)  # type = ignore
    
    cv2.imshow("canvas", img)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()