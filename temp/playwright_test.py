import asyncio
import os
from datetime import datetime

from playwright.async_api import async_playwright

# OCR 객체
# paddle_OCR = PaddleOCR(lang="korean")
# draw_ocr 메소드에 대한 글꼴 경로 지정
font = os.path.join('../', 'D2Coding-Ver1.3.2-20180524-all.ttc')

# 파싱 URL
url = "https://pf.kakao.com/_swtYxl"
profile_selector = "div.item_profile_head > button > span > img"

dir_name = datetime.today().strftime('%Y-%m-%d')


async def run(_url, _file_path) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)  # 크로미움 사용
        context = await browser.new_context()  # 새 컨텍스트 생성
        page = await context.new_page()  # 새 페이지 열기
        await page.goto(_url)  # 페이지 이동

        # 스크롤을 이용하여 지연
        # for _ in range(7):
        #     await page.keyboard.press('PageDown')
        #     await asyncio.sleep(0.5)

        # auto wait
        await page.get_by_alt_text("프로필 이미지").click()
        aa = await page.query_selector(profile_selector)
        bb = await aa.get_attribute("src")

        await context.close()  # 컨텍스트 종료
        await browser.close()  # 브라우저 종료


async def main() -> None:
    await run(url, dir_name)


asyncio.run(main())  # 실행
