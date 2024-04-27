import asyncio
import os
from datetime import datetime

import aiofiles
import aiohttp
import cv2
from bs4 import BeautifulSoup
from loguru import logger
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
from paddleocr.tools.infer.utility import draw_ocr

from util import crop_and_convert_image, get_draw_result, group_texts_by_line, get_grouped_texts

"""
lazy load라 fail
"""

# OCR 객체
paddle_OCR = PaddleOCR(lang="korean")
# draw_ocr 메소드에 대한 글꼴 경로 지정
font = os.path.join('../', 'D2Coding-Ver1.3.2-20180524-all.ttc')

# 파싱 URL
url = "https://pf.kakao.com/_swtYxl"
profile_selector = "div.item_profile_head > button > span > img"

dir_name = datetime.today().strftime('%Y-%m-%d')


async def get_menu_image_save(_url, _file_path):
    async with aiohttp.ClientSession() as _session:
        async with _session.get(_url) as resp:
            try:
                if resp.status != 200:
                    raise Exception(f"status code : {resp.status}, reason: {resp.reason}")

                res_text = await resp.text("UTF-8")
                bs = BeautifulSoup(res_text, "html.parser")
                await _get_aio_file(bs.select_one(profile_selector)['src'], _file_path)

            except Exception as e:
                logger.error(e)
                raise e
            finally:
                await _session.close()


async def _get_aio_file(_url, _file_path):
    async with aiohttp.ClientSession() as _session:
        async with _session.get(_url) as resp:
            try:
                if resp.status != 200:
                    raise Exception(f"status code : {resp.status}, reason: {resp.reason}")

                f = await aiofiles.open('/some/file.img', mode='wb')
                await f.write(await resp.read())

            except Exception as e:
                logger.error(e)
                raise e
            finally:
                await f.close()
                await _session.close()


# 탐지 영역을 시각화한 이미지 반환
def get_ocr_result_image(_image_path, boxes, texts, scores):
    # read image
    img = cv2.imread(_image_path)

    # 이미지에 주석 그리기
    annotated = draw_ocr(img, boxes, texts, scores, font_path=font)

    # matplotlib을 사용하여 이미지 저장
    plt.imsave(os.path.join('./output', dir_name, 'result.jpg'), annotated)


async def main():
    menu_image = os.path.join("./input", dir_name, "menu.jpg")
    conv_img = os.path.join('./output', dir_name, 'crop.jpg')

    await get_menu_image_save(url, menu_image)
    crop_and_convert_image(menu_image, conv_img)

    ocr_result = paddle_OCR.ocr(conv_img, cls=False)[0]

    boxes, scores, texts = await get_draw_result(ocr_result, len(ocr_result))

    lines = group_texts_by_line(boxes, texts, scores)
    grouped_texts = get_grouped_texts(lines)
    print(grouped_texts)

    get_ocr_result_image(conv_img, boxes, texts, scores)


if __name__ == "__main__":
    asyncio.run(main())
