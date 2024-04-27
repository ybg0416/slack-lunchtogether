import asyncio
import json
import os

import aiofiles
from dotenv import load_dotenv
from loguru import logger  # noqa

from util import send_slack, get_aio_json

load_dotenv()

slack_url = os.environ.get('SLACK_WEBHOOK_URL')


async def main(grouped_texts, menu_src):
    async with aiofiles.open('../slack.json', mode='r', encoding="utf-8") as f:
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
    # result = json.dumps(result, ensure_ascii=False)
    logger.info(result)
    await send_slack(slack_url, result)


if __name__ == "__main__":
    grouped_texts = ['04월 22일 월요일 점심메뉴', '잡곡밥 & 흰밥', '소고기 무국', '춘천 닭갈비', '오칭어 해물까스', '부추산적구이', '비빔 졸면',
                     '아삭이고추무침 & 그린샐러드 드레싱', '포기김치']
    asyncio.run(main(grouped_texts, "https://cataas.com/cat"))
