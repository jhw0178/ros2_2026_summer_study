from pathlib import Path

import cv2
import numpy as np

def main():
    file_path = Path(__file__).parent
    logo = cv2.imread(str(file_path / "data/logo.jpg"))
    bg = cv2.imread(str(file_path / "data/robot.jpg"))
    
    h, w, _ = logo.shape
    x, y = 10, 10
    masks = cv2.threshold(logo, 220, 255, cv2.THRESH_BINARY)[1]     #[1]은 채널 1을 사용한다는 의미
    masks = cv2.split(masks)
    
    fg_pass_mask = cv2.bitwise_or(masks[0], masks[1])
    fg_pass_mask = cv2.bitwise_or(masks[2], fg_pass_mask)
    bg_pass_mask = cv2.bitwise_not(fg_pass_mask)
    roi = bg[y : y + h, x: x + w]
    foreground = cv2.bitwise_and(logo, logo, mask = fg_pass_mask)
    background = cv2.bitwise_and(roi, roi, mask=bg_pass_mask)
    
    dst = cv2.add(background, foreground)
    bg[y : y + h, x : x + w] = dst
    
    cv2.imshow("mask", fg_pass_mask)
    cv2.imshow("background", bg)
    cv2.imshow("logo", logo)
    cv2.waitKey()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()