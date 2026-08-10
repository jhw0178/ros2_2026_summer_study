# depth + yolo 가상 환경에서 실행

from ultralytics import YOLO
import cv2


def main():
    model = YOLO("yolo26n.pt")  # load a pretrained YOLO26n model
    results = model("/home/jhw0178/ros2_2026_summer_study/AL/data/dog.jpg")  # run inference
    annotated = results[0].plot()    #type: ignore
    cv2.imshow("result", annotated)
    cv2.waitKey()
    
if __name__ == "__main__":
    main()