from tokenizer import romanize
from japanese_word import JAPANESE_WORD
import sl
import sys
import tqdm
import csv
help = '''
拆分混合的txt文件为标准格式(json,csv,txt)：
1. #是注释
2. 每个日语句子只有一行，且总是包含日语字母
3. 每个日语句子有多条中文翻译，且总是没有日语字母
4. 空行（含全空格）会被忽略
'''
continuous_token = "ー-"
cache_romanji = {}


def get_romanji(text):
    if text not in cache_romanji:
        cache_romanji[text] = romanize(text)[0]
    return cache_romanji[text]


class TERMSTATES:
    NONE = 0
    HIRAGANA = 1
    KATAKANA = 2
    KANJI = 3
    ENGLISH = 4


def find_term(line: str, terms: "dict[str,str]|list[str]|set[str]"):
    # 1. 将片假名注音
    # 2. 替换术语
    term_list = []
    current_chars = []
    current_state = TERMSTATES.NONE
    replaced = set()
    for char in list(line):
        if JAPANESE_WORD.is_hiragana_single(char):
            new_state = TERMSTATES.HIRAGANA
        elif JAPANESE_WORD.is_katakana_single(char):
            new_state = TERMSTATES.KATAKANA
        elif JAPANESE_WORD.is_kanji_single(char):
            new_state = TERMSTATES.KANJI
        elif char in continuous_token:
            new_state = current_state
        else:
            # english or token
            new_state = TERMSTATES.ENGLISH
        if current_state != TERMSTATES.NONE and new_state != current_state and len(current_chars) != 0:
            token = "".join(current_chars)
            if token in terms:
                # termlist.append(meaning)
                if token not in replaced:
                    meaning = f"[{terms[token]}]"
                    replaced.add(token)
                    line = line.replace(token, meaning)
            elif current_state == "katakana":
                # termlist.append(f"({rmj})")
                if token not in replaced:
                    replaced.add(token)
                    rmj = get_romanji(token)
                    line = line.replace(token, f"{token}({rmj})")
            current_chars = []
        current_state = new_state
        current_chars.append(char)
    return line, "".join(term_list)


def import_web_txt(path, terms):
    filedata = sl.readstr(path).splitlines()
    maxline = 1000000
    content = []
    cached_translation = []
    for line in tqdm.tqdm(filedata[:maxline]):
        line = line.strip()
        if len(line) == 0:
            pass
        else:
            if line[0] == "#":
                content.append({
                    "type": "comment",
                    "content": line,
                })
            elif JAPANESE_WORD.has_japanese(line):
                line, term = find_term(line, terms)
                content.append({
                    "type": "sentence",
                    "content": line,
                    "term": term,
                    "translation": cached_translation[:],
                })
                cached_translation = []
            else:
                cached_translation.append(line)
    return content


maxlines = 10000


def export_txt(data, path):
    lines = []
    num = 1
    for item in data:
        if item['type'] == "comment":
            if len(lines) > maxlines:
                sl.writestr(path.replace('.txt', '') +
                            "."+str(num)+".txt", lines)
                num += 1
                lines.clear()
            lines.append(item['content'])
        else:
            lines.append('\n')
            lines.append(item['content'])
            if len(item['term']) > 0:
                lines.append(item['term'])
            for translation in item['translation']:
                lines.append(translation)


def export_csv(data, path):
    id = 1
    cnt = 0
    num = 1
    f = open(path.replace('.csv', '') +
             "."+str(num)+".csv", 'w', encoding='utf-8')
    writer = csv.DictWriter(
        f, fieldnames=['key', 'original',  'translation'])
    writer.writeheader()
    for item in data:
        if cnt > maxlines:
            f.close()
            cnt = 0
            num += 1
            f = open(path.replace('.csv', '') +
                     "."+str(num)+".csv", 'w', encoding='utf-8')
            writer = csv.DictWriter(
                f, fieldnames=['key', 'original',  'translation'])
            writer.writeheader()
        cnt += 1
        if item['type'] == "sentence":
            writer.writerow({
                "key": id,
                "original": item['content'],
                "translation": '\n'.join(item['translation'])
            })
        elif item['type'] == "comment":
            writer.writerow({
                "key": id,
                "original": item['content'],
                "translation": item['content'],
            })
        id += 1


def import_txt(path):
    data = sl.readstr(path).splitlines()
    lines = []
    c = {
        "type": "sentence",
        "content": "",
        "term": "",
        "translation": [],
    }
    for line in data:
        if len(line) > 0 and line[0] == "#":
            lines.append({
                "type": "comment",
                "content": line
            })
        elif len(line) == 0 and len(c["content"]) > 0:
            lines.append(c)
            c = {
                "type": "sentence",
                "content": "",
                "term": "",
                "translation": [],
            }
        elif JAPANESE_WORD.has_japanese(line) and len(c["content"]) == 0:
            c["content"] = line
        else:
            c["translation"].append(line)


def export_json(data, path):
    return sl.save_json(path, data, True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(
            "Usage: python3 split.py <file_web.txt> <term.json[str,str]> <output_format:txt|csv|json> <split_lines:10000>")
        print(help)
        exit(1)
    term = sl.load_json(sys.argv[2])
    filename = sys.argv[1]
    filen = filename[:-3]
    maxlines = int(sys.argv[4]) if len(sys.argv) >= 5 else 10000
    fmt = sys.argv[3]
    data = import_web_txt(filename, term)
    sl.save_json(filen+"term.json", cache_romanji)
    if fmt == "txt":
        export_txt(data, filen+"export.txt")
    elif fmt == "csv":
        export_csv(data, filen+"export.csv")
    elif fmt == "json":
        export_json(data, filen+"export.json")
    else:
        print("Unknown format: {}".format(fmt))
