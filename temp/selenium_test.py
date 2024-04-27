import asyncio
import os
from datetime import datetime

from arsenic import get_session
from arsenic.browsers import Chrome, Firefox
from arsenic.services import Chromedriver, Geckodriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# OCR 객체
# paddle_OCR = PaddleOCR(lang="korean")
# draw_ocr 메소드에 대한 글꼴 경로 지정
font = os.path.join('../', 'D2Coding-Ver1.3.2-20180524-all.ttc')

# 파싱 URL
url = "https://pf.kakao.com/_swtYxl"
profile_selector = "div.item_profile_head > button > span > img"

dir_name = datetime.today().strftime('%Y-%m-%d')


async def get_menu_image_save(_url, _file_path):  # 크롬 드라이버 생성
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # 3초 대기 설정 (lazy loading)
    driver.implicitly_wait(3)

    async with get_session(Chromedriver(ChromeService(ChromeDriverManager().install())), Chrome()) as session:
        # 페이지 접속
        await session.get(_url)
        # a = session.find_element(By.CSS_SELECTOR, profile_selector)
        # print(a.get_attribute('src'))
    # res_text = await resp.text("UTF-8")
    # bs = BeautifulSoup(res_text, "html.parser")
    # await _get_aio_file(bs.select_one(profile_selector)['src'], _file_path)


asyncio.run(get_menu_image_save(url, dir_name))
