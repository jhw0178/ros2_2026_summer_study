# box filter와 blur

from pathlib import Path
import cv2
import numpy as np

def main():
    file_path = Path(__file__).parent
    file_path = file_path / "data/lena.jpg"
    img: np.ndarray = cv2.imread(str(file_path))   # type: ignore
    # boxfilter
    dst1 = cv2.boxFilter(img, ddepth=-1, ksize=(11, 11))    # k는 홀수로만
    # blur
    dst2 = cv2.blur(img, (11, 11))
    # filter 2D
    kernel = np.ones((11, 11)) / 11
    dst3 = cv2.filter2D(img, ddepth=-1, kernel=kernel)
    
    # 실행시 창 띄우기
    cv2.imshow("img", img)
    cv2.imshow("box11", dst1)
    cv2.imshow("blur", dst2)
    cv2.imshow("filter2D", dst3)
    cv2.waitKey()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()