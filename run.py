import asyncio
import logging.handlers
import os
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger
from paddleocr import PaddleOCR

from util import (crop_and_convert_image, get_draw_result, group_texts_by_line, get_grouped_texts, get_ocr_result_image,
                  get_slack_message, send_slack, get_menu_image_save)

logging.getLogger('ppocr').setLevel(logging.INFO)  # noqa OCR 관련 로그 레벨
logger.add("menu.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="DEBUG", retention="10 days")

logger.info("start")

load_dotenv()
# OCR 객체
paddle_OCR = PaddleOCR(lang="korean")
# draw_ocr 메소드에 대한 글꼴 경로 지정
font = os.path.join("./fonts", os.environ.get('FONT'))

# 파싱 URL
url = os.environ.get('URL')
# submit url
slack_url = os.environ.get('SLACK_WEBHOOK_URL')
profile_selector = os.environ.get("PROFILE_SELECTOR")

# 폴더 생성
dir_name = datetime.today().strftime('%Y-%m-%d')
dir_input, dir_output = [os.path.join(os.environ.get("input_dir"), dir_name),
                         os.path.join(os.environ.get("output_dir"), dir_name)]

os.makedirs(dir_input, exist_ok=True)
os.makedirs(dir_output, exist_ok=True)

# 디버깅용
is_slack_submit = True
is_menu_download = True


async def main():

    menu_src = None
    menu_image = os.path.join(dir_input, "menu.jpg")
    conv_img = os.path.join(dir_output, 'crop.jpg')

    # 이미지 다운로드 및 변환
    if is_menu_download:
        menu_src = await get_menu_image_save(url, profile_selector, menu_image)
    crop_and_convert_image(menu_image, conv_img)

    # OCR runn
    try:
        ocr_result = paddle_OCR.ocr(conv_img, cls=False)[0]
        if not ocr_result:
            raise Exception("OCR Result Invalid")
    except Exception as e:
        raise e

    boxes, texts, scores = get_draw_result(ocr_result, len(ocr_result))
    logger.info("추출 문자열 :{}", texts)

    # 파싱한 텍스트 분리 및 결합
    lines = group_texts_by_line(boxes, texts)
    grouped_texts = get_grouped_texts(lines)

    # 메뉴 이미지가 아닌 경우 (간판)
    if "런치투게더" in grouped_texts:
        raise Exception("Not A Menu Image")

    logger.info("최종 추출 결과물 : {}", grouped_texts)

    # OCR result image 출력, 발송
    if menu_src and is_slack_submit :
        get_ocr_result_image(conv_img, dir_output, boxes, texts, scores, font)
        await send_slack(slack_url, await get_slack_message(grouped_texts, menu_src))


if __name__ == "__main__":
    asyncio.run(main())
