import romaji_jp
from japanese_word import JAPANESE_WORD
import requests
from bs4 import BeautifulSoup
import mdict
import tokenizer
import re
from cache import CACHE
from baidutrans import translate_baidu as translate
# from translator import translate
from ai import talk_to_ai, msg_memorize, msg_explain
from functools import lru_cache
c = CACHE()


def get_explanation(sentence, web):
    sentence = sentence.strip()\
        .replace('\r\n', '\n')\
        .replace('  ', ' ')\
        .replace('  ', ' ')\
        .replace('  ', ' ')\
        .replace('  ', ' ')
    result = talk_to_ai(sentence, msg_explain, web)
    return result


def get_memorization(word, web):
    result = talk_to_ai(word, msg_memorize, web)
    return result


def get_translation(sentence):
    ret = None
    if not sentence:
        return ""
    try:
        # ret = translate(sentence, "jp", "zh")
        ret = translate(sentence, dest='zh', src='jp')
    except Exception as e:
        print("Translation Error")
        print(e)
        return ""
    if not ret:
        return ""
    return ret


alphabet = '。、，？！…,."\'“‘;:：；【】{}[]》「」『』｢｣·･（）()'


def preproc(text, is_sentence=False):
    text = text.strip()
    if is_sentence and len(text) > 0:
        last_c = text[-1]
        if last_c and last_c not in alphabet:
            text += '。'
    return text


def process_query(text, trans, lookup):
    if not text:
        return {"success": False}
    text = preproc(text)
    if len(text) == 0:
        return {"success": False}
    texts = re.split("。|\n", text)
    results = []
    for i in texts:
        proc_text = preproc(i, True)
        if proc_text:
            results.append(process_string(proc_text, trans, lookup))
    return {"success": True, "data": results, "translation": get_translation(text) if trans else None, "lookup": get_meaning(text) if lookup else None}


def process_lookup(text):
    if not text:
        return {"success": False, "reason": "no text"}
    _text = text
    text = preproc(text)
    if len(text) == 0:
        return {"success": False, "reason": "blank text"}
    meaning = get_meaning(text)
    weblio = lookup_weblio(text)
    jisho = lookup_jisho(text)
    if not meaning:
        meaning = ""
    if jisho:
        meaning += jisho
    if weblio:
        meaning += weblio
    return {"success": True, "data": {"text": _text, "content": meaning}}


def process_lookuppinyin(text):
    if not text:
        return {"success": False}
    text = preproc(text)
    text = romaji_jp.romaji_to_japanese(text)
    text = JAPANESE_WORD.chinese_to_japanese(text)
    ret = process_lookup(text)
    ret["text"] = text
    return ret


def process_string(text, trans, lookup):
    tokens = c.get(text)
    if not tokens:
        tokens = tokenizer.tokenize(text)
        if len(tokens) > 0 and not isinstance(tokens[0], dict):
            tokenjson = [tokenizer.TOKENIZER.json(i) for i in tokens]
        else:
            tokenjson = tokens
        c.set(text, tokenjson)
        tokens = tokenjson
    romajis = tokenizer.romanize_list(tokens)
    for i in range(len(tokens)):
        tokens[i]["romaji"] = romajis[i]
    return {"text": text, "tokens": tokens, "translation": get_translation(text) if trans else None, "lookup": get_meaning(text) if lookup else None}


md = mdict.MDICT()
md.load_json()
md.textify = lambda text: text


def get_meaning(token):
    return md.find(token)


def lookup_weblio(word):
    url = f"https://www.weblio.jp/content/{word}"

    # 发起请求获取HTML文档
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # 找到所有<div class="kiji">
            articles = soup.find_all('div', class_='kiji')
            # 合并为一个子HTML字符串
            result_html = ''.join([str(article) for article in articles])
            return result_html
    except:
        pass
    return None


def process_jisho(text):
    text = text.replace("Ichidan verb", "一段")
    text = text.replace("Godan verb", "五段")
    text = text.replace("Intransitive verb", "不及物")
    text = text.replace("Transitive verb", "及物")
    text = text.replace(" with '", "以")
    text = text.replace("' ending", "结尾")
    text = text.replace("Other forms", "其他形式")
    text = text.replace("Notes", "注释")
    text = text.replace("Rarely-used kanji form", "罕用汉字")
    text = text.replace("taking the '", "后跟")
    text = text.replace("' particle", "词")
    text = text.replace("Adverb (fukushi)", "副词")
    text = text.replace("Adverb", "副词")
    text = text.replace("Noun", "名词")
    text = text.replace("See also", "参见")
    return text


def lookup_jisho(word):
    url = f"https://jisho.org/search/{word} #words"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div1 = soup.find(
                'div', class_='concept_light-wrapper columns zero-padding')
            text = ""
            if div1:
                text += str(div1)
            div2 = soup.find(
                'div', class_='concept_light-meanings medium-9 columns')
            if div2:
                text += str(div2)
            if text:
                return process_jisho(text)
    except:
        pass
    return None
