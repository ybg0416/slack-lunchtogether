import base64
import json
import os
import re

import aiofiles
import aiohttp
import cv2
from PIL import Image
from loguru import logger
from matplotlib import pyplot as plt
from paddleocr.tools.infer.utility import draw_ocr
from playwright.async_api import async_playwright

and_pattern = re.compile('([ㄱ-힣])&')


async def get_menu_image_save(url, profile_selector, file_path) -> str:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()  # 크로미움 사용
        context = await browser.new_context()  # 새 컨텍스트 생성
        page = await context.new_page()  # 새 페이지 열기
        await page.goto(url)  # 페이지 이동

        # auto wait
        await page.get_by_alt_text("프로필 이미지").click()
        src = await (await page.query_selector(profile_selector)).get_attribute("src")
        await get_aio_file(src, file_path)
        await context.close()  # 컨텍스트 종료
        await browser.close()  # 브라우저 종료
        return src


async def get_aio_json(url) -> dict[str, str | list[str]]:
    async with aiohttp.ClientSession() as _session:
        async with _session.get(url) as resp:
            try:
                if resp.status != 200:
                    raise Exception(f"status code : {resp.status}, reason: {resp.reason}")
                return await resp.json()

            except Exception as e:
                logger.error(e)
                raise e
            finally:
                await _session.close()


async def get_aio_image_to_base64(file_path, string=True) -> str | bytes:
    try:
        async with aiofiles.open(file_path, mode='rb') as f:
            r = await f.read()
            encoded_string = base64.b64encode(r)
            if string:
                return encoded_string.decode('utf-8')
            return encoded_string
    except Exception as e:
        raise e
    finally:
        await f.close()


async def get_aio_file(url, file_path) -> None:
    async with aiohttp.ClientSession() as _session:
        async with _session.get(url) as resp:
            try:
                if resp.status != 200:
                    raise Exception(f"status code : {resp.status}, reason: {resp.reason}")

                f = await aiofiles.open(file_path, mode='wb')
                await f.write(await resp.read())
                await f.close()

            except Exception as e:
                logger.error(e)
                raise e
            finally:
                await _session.close()


# 이미지 수정 작업 수행
def crop_and_convert_image(in_path, out_path, fmt_type="jpeg") -> None:
    image = Image.open(in_path)
    image = image.convert("L")
    w, h = image.size
    image = image.crop((0, 280, w, h - 100))
    image.save(out_path, fmt_type)
    image.close()


def get_draw_result(ocr_result, result_size) -> (list, list, list):
    boxes = [ocr_result[i][0] for i in range(result_size)]
    texts = [ocr_result[i][1][0] for i in range(result_size)]
    scores = [float(ocr_result[i][1][1]) for i in range(result_size)]
    return boxes, texts, scores


# 문자열의 중앙 값으로 높이를 파악하여 같은 줄에 있는 문자열을 그룹화하는 함수
def group_texts_by_line(boxes, texts, threshold=10) -> [[str]]:
    lines = []
    current_line = []
    current_line_y = None
    current_line_x_max = None
    for i, (box, text) in enumerate(zip(boxes, texts)):
        x_min, y_min, x_max, y_max = box
        x_center = (x_min[0] + x_max[0]) / 2  # 상자의 좌표에서 x 좌표만 추출하여 계산
        y_center = (y_min[1] + y_max[1]) / 2  # 상자의 좌표에서 y 좌표만 추출하여 계산

        # 이전 문자열과의 중앙 y 값 차이 계산
        y_diff = abs(y_center - current_line_y) if current_line_y is not None else None

        # y 중앙 값, 증가한 x로 문자열 그룹화 판단
        if current_line_y is None or (y_diff is not None and y_diff < threshold and x_center > current_line_x_max):
            current_line.append(text)
        else:
            # 김 & 밥 -> [[a,&,c]] -> [[a b c]]
            if text.startswith("&") or current_line[-1].endswith("&"):
                current_line[-1] += " " + text
            else:
                lines.append(current_line)
                current_line = [text]
        current_line_y = y_center
        current_line_x_max = x_max[0]

    if current_line:
        lines.append(current_line)
    return lines


# 그룹화된 문자열을 리스트로 반환하는 함수
def get_grouped_texts(lines) -> [str]:
    # grouped_texts = []
    # for line in lines:
    #     grouped_texts.append(' '.join(line))

    return [' '.join(line) for line in lines]


# 탐지 영역을 시각화한 이미지 반환
def get_ocr_result_image(image_path, dir_output, boxes, texts, scores, font) -> None:
    # read image
    img = cv2.imread(image_path)

    # 표시 영역 크기 조정
    plt.figure(figsize=(65, 65))

    # 이미지에 주석 그리기
    annotated = draw_ocr(img, boxes, texts, scores, font_path=font)

    # matplotlib을 사용하여 이미지 저장
    plt.imsave(os.path.join(dir_output, 'result.jpg'), annotated)


async def get_slack_message(grouped_texts, menu_src) -> str:
    async with aiofiles.open('slack.json', mode='r', encoding="utf-8") as f:
        contents = await f.read()
        result = json.loads(contents)
    # title
    result["blocks"][0]["text"]["text"] = grouped_texts[0]

    # menu image
    result["blocks"][2]["image_url"] = menu_src

    # menu
    result["blocks"][3]["text"]["text"] = ""
    for _, text in enumerate(grouped_texts[1:]):
        result["blocks"][3]["text"]["text"] += text + "\r\n"
    # dog
    result["blocks"][6]["elements"][0]["image_url"] = (await get_aio_json("https://dog.ceo/api/breeds/image/random"))[
        "message"]

    return result


async def send_slack(url, _json) -> None:
    async with aiohttp.ClientSession() as client:
        async with client.post(url, json=_json) as resp:
            res = await resp.text()
            logger.info(res)
