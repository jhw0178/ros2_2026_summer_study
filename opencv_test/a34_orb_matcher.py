from pathlib import Path

import cv2
import numpy as np

data_dir = Path(__file__).resolve().parent / "data"
file_path1 = data_dir / "book1.jpg"
file_path2 = data_dir / "book2.jpg"
src1 = cv2.imread(str(file_path1), cv2.IMREAD_COLOR)
src2 = cv2.imread(str(file_path2), cv2.IMREAD_COLOR)
if src1 is None:
    raise FileNotFoundError(f"첫 번째 이미지를 불러올 수 없습니다: {file_path1}")
if src2 is None:
    raise FileNotFoundError(f"두 번째 이미지를 불러올 수 없습니다: {file_path2}")
img1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)


# ORB 특징점 및 기술자 계산
orb = cv2.ORB_create(nfeatures=1000)
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)
print(f"첫 번째 영상 특징점 수: {len(kp1)}")
print(f"두 번째 영상 특징점 수: {len(kp2)}")
if des1 is None or len(kp1) == 0:
    raise RuntimeError("첫 번째 영상에서 ORB 특징점을 검출하지 못했습니다.")
if des2 is None or len(kp2) == 0:
    raise RuntimeError("두 번째 영상에서 ORB 특징점을 검출하지 못했습니다.")

# 3. 기술자 매칭
# ORB는 이진 기술자이므로 Hamming 거리를 사용
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True,)
matches = bf.match(des1, des2)
if len(matches) == 0:
    raise RuntimeError("두 영상 사이의 매칭 결과가 없습니다.")
# 거리가 작을수록 유사한 매칭
matches = sorted(matches,key=lambda match: match.distance,)
print(f"전체 매칭 개수: {len(matches)}")
for index, match in enumerate(matches[:3]):
    print(f"matches[{index}]=" f"(queryIdx:{match.queryIdx}, " f"trainIdx:{match.trainIdx}, " f"distance:{match.distance})")

# 4. 좋은 매칭 선택
min_distance = matches[0].distance
# 최솟값이 0이면 5 * min_distance도 0이 되어
# 어떤 매칭도 선택되지 않을 수 있으므로 최소 기준을 추가
distance_threshold = max(5.0 * min_distance, 30.0,)
good_matches = [match
    for match in matches
    if match.distance <= distance_threshold
]
print(f"최소 거리: {min_distance}")
print(f"거리 기준: {distance_threshold}")
print(f"좋은 매칭 개수: {len(good_matches)}")
# 호모그래피에는 최소 4쌍의 점이 필요하지만,
# 안정성을 위해 여기서는 5개 이상을 요구
if len(good_matches) < 5:
    raise RuntimeError("호모그래피 계산에 사용할 좋은 매칭이 부족합니다.")

# 5. RANSAC 적용 전 매칭 결과
match_view = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,)
cv2.imshow("Good Matches", match_view)

# 6. 대응점 좌표 생성
src1_pts = np.float32([kp1[match.queryIdx].pt for match in good_matches]).reshape(-1, 1, 2)
src2_pts = np.float32([kp2[match.trainIdx].pt for match in good_matches]).reshape(-1, 1, 2)

# 7. RANSAC을 이용한 호모그래피 계산
H, mask = cv2.findHomography(src1_pts, src2_pts, cv2.RANSAC, 3.0)
if H is None or mask is None:
    raise RuntimeError("호모그래피를 계산하지 못했습니다. " "잘못된 매칭이 많거나 대응점 배치가 적절하지 않습니다.")
inlier_mask = mask.ravel().tolist()
print(f"RANSAC 인라이어 개수: {sum(inlier_mask)}")

# 8. 첫 번째 영상의 외곽선을 두 번째 영상에 투영
height, width = img1.shape
corners = np.float32([[0, 0], [0, height - 1], [width - 1, height - 1], [width - 1, 0],]).reshape(-1, 1, 2)
transformed_corners = cv2.perspectiveTransform(corners, H,)
src2_result = src2.copy()
cv2.polylines(src2_result, [np.int32(transformed_corners)], isClosed=True, color=(255, 0, 0), thickness=2)

# 9. RANSAC 인라이어 매칭만 출력
draw_params = {"matchColor": (0, 255, 0), "singlePointColor": None, "matchesMask": inlier_mask, "flags": cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS}
result = cv2.drawMatches(src1, kp1, src2_result, kp2, good_matches, None, **draw_params)

cv2.imshow("ORB Homography", result)
cv2.waitKey(0)
cv2.destroyAllWindows()