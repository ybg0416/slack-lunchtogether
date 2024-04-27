import os

from PIL import Image

img_path = os.path.join('./input', 'test.jpg')

image = Image.open(img_path)
# 이미지 수정 작업 수행
black_and_white_image = image.convert("L")
w, h = black_and_white_image.size
black_and_white_image = black_and_white_image.crop((0, 280, w, h-100))

black_and_white_image.save("bw_test.jpg", "jpeg")
# plt.imshow(img_np)
# plt.show()
