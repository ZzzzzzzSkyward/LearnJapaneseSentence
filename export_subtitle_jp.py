from subtitle import SUBTITLE
import os


def export():
    jsons = os.listdir()
    jsons = [i for i in jsons if i.endswith('ass.json')]
    texts = set()
    for json in jsons:
        s = SUBTITLE()
        s.load_json(json)
        for i in s.lines:
            if i[0] == "jp" and len(i[1]) > 2:
                texts.add(i[1])
    with open('export.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(texts))

if __name__ == '__main__':
    export()