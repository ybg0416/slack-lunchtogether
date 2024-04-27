import os  # folder directory navigation

import cv2  # opencv
from matplotlib import pyplot as plt  # plot images
from paddleocr import PaddleOCR
from paddleocr.tools.infer.utility import draw_ocr

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'  # 이거 안해주면 오류남

ocr = PaddleOCR(lang="korean")

# img_path = "img_xl.jpg"
img_path = os.path.join('../', 'test_crop.jpg')
"""
img: img for OCR, support ndarray, img_path and list or ndarray
det: use text detection or not. If False, only rec will be exec. Default is True
rec: use text recognition or not. If False, only det will be exec. Default is True
cls: use angle classifier or not. Default is True. If True, the text with rotation of 180 degrees can be recognized. 
If no text is rotated by 180 degrees, use cls=False to get better performance. 
Text with rotation of 90 or 270 degrees can be recognized even if cls=False.
bin: binarize image to black and white. Default is False.
inv: invert image colors. Default is False.
alpha_color: set RGB color Tuple for transparent parts replacement. Default is pure white.
"""
result = ocr.ocr(img_path, cls=False)

ocr_result = result[0]
print(ocr_result)
print(type(ocr_result))
boxes = [ocr_result[i][0] for i in range(len(result[0]))]  #
texts = [ocr_result[i][1][0] for i in range(len(result[0]))]
scores = [float(ocr_result[i][1][1]) for i in range(len(result[0]))]
# for res in result:
print(boxes[0])
print(texts[0])
print(scores[0])  # , Text: {res[1]}

# Specifying font path for draw_ocr method
font_path = os.path.join('../', 'D2Coding-Ver1.3.2-20180524-all.ttc')

# imports image
img = cv2.imread(img_path)

# 색상 채널을 재정렬 -> OpenCV의 imread는 RGB가 아니라 BGR인데, 이유는 개발 당시 그걸 많이 써서.
# 흑백 변환한 이미지라 노상관
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# 이미지와 탐지를 시각화합니다.
# 표시 영역 크기 조정 -> 안해도 정상 동작함..
# plt.figure(figsize=(65, 65))

# draw annotations on image
annotated = draw_ocr(img, boxes, texts, scores, font_path=font_path)

# show the image using matplotlib
# plt.imshow(annotated)
plt.imsave("test.jpg", annotated)
