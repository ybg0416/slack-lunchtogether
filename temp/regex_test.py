# paddleocr --image_dir ./img_xl --lang=korean
# https://pypi.org/project/paddleocr/
import re

if __name__ == '__main__':
    aaaa = "김& 밥"
    result = re.search('([ㄱ-힣])&', aaaa)

    if result:
        print(re.sub('([ㄱ-힣])&', result.group(1) +" &", aaaa))
