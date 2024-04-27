import os
from PIL import Image
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="korean")


# 이미지 수정 작업 수행
def crop_and_convert_image(in_path, out_path, fmt_type="jpeg") -> None:
    image = Image.open(in_path)
    image = image.convert("L")
    w, h = image.size
    image = image.crop((0, 280, w, h - 100))
    image.save(out_path, fmt_type)
    image.close()


# 문자열의 중앙 값으로 높이를 파악하여 같은 줄에 있는 문자열을 그룹화하는 함수
def group_texts_by_line(boxes, texts, scores):
    lines = []
    current_line = []
    current_line_y = None
    for box, text, score in zip(boxes, texts, scores):
        x_min, y_min, x_max, y_max = box
        y_center = (y_min[1] + y_max[1]) / 2  # 상자의 좌표에서 y 좌표만 추출하여 계산
        if current_line_y is None or abs(y_center - current_line_y) < 30:  # 임의의 값인 30을 사용하여 같은 줄로 간주
            current_line.append((box, text))
            current_line_y = y_center
        else:
            lines.append(current_line)
            current_line = [(box, text)]
            current_line_y = y_center
    if current_line:
        lines.append(current_line)
    return lines


# 그룹화된 문자열을 합쳐서 출력하는 함수
def print_grouped_texts(lines):
    for line in lines:
        line_text = ' '.join([text for _, text in line])
        print(line_text)


if __name__ == '__main__':
    img_path = os.path.join('../input', 'test.jpg')
    crop_img = os.path.join('../output', 'crop_image.jpg')

    crop_and_convert_image(img_path, crop_img)

    result = ocr.ocr(crop_img, cls=False)

    ocr_result = result[0]

    boxes = [ocr_result[i][0] for i in range(len(result[0]))]
    texts = [ocr_result[i][1][0] for i in range(len(result[0]))]
    scores = [float(ocr_result[i][1][1]) for i in range(len(result[0]))]
    print(texts)
    lines = group_texts_by_line(boxes, texts, scores)
    print_grouped_texts(lines)
