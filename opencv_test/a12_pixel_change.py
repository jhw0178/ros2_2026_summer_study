from pathlib import Path
import cv2

def main():
    file_path = Path(__file__).parent
    img = cv2.imread(str(file_path / "data/lena.jpg"), cv2.IMREAD_GRAYSCALE) # GRAYSCALE로 가져오기
    
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img", img.shape[1], img.shape[0])
    
    print(img[100, 200])
    # img[100, 200] = 0 # x = 200, y = 100 # numpy에서 제공하는 interface임 헷갈리지 말기
    # img[100][200] = 0 # 기존의 interface
    
    # for 문은 너무 비효율적임 (slicing이 나음)
    # for y in range(100, 400):
    #    for x in range(200, 300):
    #        img[y, x] = 0
    
    # slicing
    img[100:400, 200:300] = 0        
    
    print(img[100, 200])
    
    
    cv2.imshow("img", img)
    cv2.waitKey() 
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()