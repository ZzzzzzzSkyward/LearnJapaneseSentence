import time
import hashlib
import requests
import uuid
from cache import CACHE
from config import config as cfg
config = cfg.baidu
c = CACHE()
c.name = "baidutranslation.json"


def generate_salt():
    return str(uuid.uuid4())


def generate_md5(appid, text, salt, secret):
    str_to_sign = f"{appid}{text}{salt}{secret}"
    return hashlib.md5(str_to_sign.encode('utf-8')).hexdigest()


last_query_time = 0
cooldown = 1


def should_wait():
    now = time.time()
    global last_query_time
    if now-last_query_time < cooldown:
        return True
    else:
        last_query_time = now
        return False


def get(*args, **kwargs):
    if should_wait():
        time.sleep(cooldown)
    global last_query_time
    last_query_time = time.time()

    return requests.get(*args, **kwargs)


recharge_info = "recharge"


def translate_baidu(text, src='jp', dest='zh', config=config):
    if c.get(text):
        return c.get(text)
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    appid, secret = config.appid, config.secret

    if not appid or not secret:
        raise ValueError("Please configure appid and secret")

    salt = generate_salt()
    sign = generate_md5(appid, text, salt, secret)

    params = {
        'q': text,
        'from': src,
        'to': dest,
        'appid': appid,
        'salt': salt,
        'sign': sign,
    }

    response = get(url, params=params)
    if response.ok:
        result = response.json()
        trans_result = result.get('trans_result')
        if trans_result:
            target = '\n'.join([trans_item['dst']
                               for trans_item in trans_result])
            return target.strip()
        else:
            print(
                f"Error in translation result: {response.json()}, param:{params}")
            if recharge_info in response.text:
                return None
            return False
    else:
        print(
            f"Http Request Error\nHttp Status: {response.status_code}\n{response.text}")
        return None


if __name__ == '__main__':
    translation = translate_baidu('Hello, world!', 'en', 'zh', config)
    print(translation)
