from pathlib import Path
import cv2

def main():
    file_path = Path(__file__).parent
    img = cv2.imread(str(file_path / "data/lena.jpg"), cv2.IMREAD_COLOR) # 원하는 COLOR로 가져오기
    
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img", img.shape[1], img.shape[0])
    
    print(img[100, 200, 0:3])
    print(type(img[100, 200, 0:3]))     # chanel 크기인 0:2는 생략 가능
    
    # slicing
    img[100:400, 200:300, 0:3] = (0, 0, 255) # 슬라이싱 한 부분에 원하는 색 지정
    
    print(img[100, 200])
    
    
    cv2.imshow("img", img)
    cv2.waitKey() 
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()