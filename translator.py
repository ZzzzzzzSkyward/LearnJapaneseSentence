'''
通用翻译接口
现在用免费的谷歌翻译
'''
import httpx
from googletrans import Translator
import asyncio
proxies = "http://localhost:7890"
_temp_client = httpx.Client(proxy=proxies)
_translator = Translator()
_translator.client._mounts = _temp_client._mounts
del _temp_client


def translate(text, *args, **kwds):
    return asyncio.run(_translator.translate(text, *args, **kwds)).text


if __name__ == '__main__':
    print(translate('你好', src='zh-cn', dest='en').text)
