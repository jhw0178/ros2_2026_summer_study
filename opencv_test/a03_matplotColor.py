# matplotlib를 사용하여 OpenCV로 읽은 이미지를 화면에 출력하는 예제

# pip install matplotlib

from pathlib import Path

import cv2
import numpy as np
from matplotlib import pyplot as plt

def main():
    file_path = Path(__file__).parent
    img = cv2.imread(str(file_path / "data/robot.jpg"))
    cv2.imshow("robot", img)
    img.resize([400, 400, 3])
    plt.axis("off")
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # OpenCV는 BGR, matplotlib는 RGB
    plt.imshow(imgRGB)
    plt.title("matplot complete")
    key = cv2.waitKey(30)
    plt.show()
    
    if key == ord("q"):
        raise KeyboardInterrupt
    
if __name__ == "__main__":
    main()