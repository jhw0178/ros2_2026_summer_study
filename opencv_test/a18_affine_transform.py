# 사진을 회전하는 함수 사용 연습

from pathlib import Path
import cv2
import numpy as np
    


def main():
    file_path = Path(__file__).parent
    img = cv2.imread(str(file_path / "data/lena.jpg"))
    
    M1 = cv2.getRotationMatrix2D(np.array(img.shape[:2]) / 2, 45, 0.6)
    M2 = cv2.getRotationMatrix2D(np.array(img.shape[:2]) / 2, -45, 0.8)
    
    # affinetransform
    pts1 = np.array([[0, 0], [1, 0], [1, 1]], dtype=np.float32)
    pts2 = np.array([[0, 0], [1.3, 0], [0.7, 0.8]], dtype=np.float32)
    M3 = cv2.getAffineTransform(pts1, pts2)
    
    dst1 = cv2.warpAffine(img, M1, np.array(img.shape[:2]))
    dst2 = cv2.warpAffine(img, M2, np.array(img.shape[:2]))
    dst3 = cv2.warpAffine(img, M3, np.array(img.shape[:2]))
    
    print(M1, type(M1))
    print(M2, type(M2))
    
    cv2.imshow("img", img)
    cv2.imshow("dist1", dst1)
    cv2.imshow("dist2", dst2)
    cv2.imshow("dist3", dst3)
    
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()